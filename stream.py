"""
stream.py — Server-Sent Events (SSE) streaming logic.

Functions:
  empty_response()         — SSE payload for a missing/empty query
  generate(query, cached)  — yields SSE events, one product at a time,
                             fetching Amazon (up to 20 pages) in parallel batches
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import scraper
import cache

MAX_PAGES = 20
BATCH_SIZE = 5


def _sse(payload: dict) -> str:
    return f'data: {json.dumps(payload)}\n\n'


def _fetch_page(url: str) -> list[dict]:
    html = scraper.fetch_page(url)
    products = scraper.parse_products(html) if html else []
    for p in products:
        p["source"] = "Amazon"
    return products


def _page_urls(base_url: str, pages: range) -> list[str]:
    return [
        base_url if page == 1 else f"{base_url}&page={page}"
        for page in pages
    ]


def empty_response() -> str:
    return _sse({"type": "done", "total": 0})


def generate(query: str, cached: list | None):
    """Yield SSE events for all products matching the search query.

    Fast path — results already in cache:
        Streams every product instantly, then sends a 'done' event.

    Slow path — nothing cached yet:
        Fetches Amazon (up to 20 pages) in parallel batches of 5.
        Each batch streams to the browser as soon as it finishes.
        Stops early if a batch returns no products.

    Event shapes:
        {"type": "product", "item": {...}}  — one product
        {"type": "done",    "total": N}     — signals end of stream
    """
    if cached is not None:
        for product in cached:
            yield _sse({"type": "product", "item": product})
        yield _sse({"type": "done", "total": len(cached)})
        return

    base_url = scraper.build_search_url(query)
    all_products = []

    for batch_start in range(1, MAX_PAGES + 1, BATCH_SIZE):
        pages = range(batch_start, min(batch_start + BATCH_SIZE, MAX_PAGES + 1))
        urls = _page_urls(base_url, pages)

        batch_products = []
        with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            futures = {executor.submit(_fetch_page, url): url for url in urls}
            for future in as_completed(futures):
                products = future.result()
                batch_products.extend(products)
                print(f"[stream] batch: {len(products)} products")
                for product in products:
                    yield _sse({"type": "product", "item": product})

        all_products.extend(batch_products)

        if not batch_products:
            print(f"[stream] pages {list(pages)} empty, stopping.")
            break

    print(f"[stream] total: {len(all_products)} products")
    cache.set(query, all_products)
    yield _sse({"type": "done", "total": len(all_products)})
