"""
stream.py — Server-Sent Events (SSE) streaming logic.

Two functions:
  empty_response()         — SSE payload for a missing/empty query
  generate(query, cached)  — yields SSE events, one product at a time,
                             fetching Amazon (3 pages) in parallel
"""

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

import scraper
import cache


def empty_response() -> str:
    """Return a single SSE 'done' event with zero results."""
    return f'data: {json.dumps({"type": "done", "total": 0})}\n\n'


def generate(query: str, cached: list | None):
    """Yield SSE events for all products matching the search query.

    Fast path — results already in cache:
        Streams every product instantly, then sends a 'done' event.

    Slow path — nothing cached yet:
        Fetches Amazon (3 pages) simultaneously using threads.
        Each batch is streamed to the browser as soon as that fetch
        finishes. The combined result is saved to cache when all done.

    Event shapes:
        {"type": "product", "item": {...}}  — one product
        {"type": "done",    "total": N}     — signals end of stream
    """
    # ── Fast path ──────────────────────────────────────────────────────────
    if cached is not None:
        for product in cached:
            yield f'data: {json.dumps({"type": "product", "item": product})}\n\n'
        yield f'data: {json.dumps({"type": "done", "total": len(cached)})}\n\n'
        return

    # ── Slow path: fetch Amazon in parallel ──────────────────────────────────
    amazon_base = scraper.build_search_url(query)

    urls = [
        amazon_base,
        f"{amazon_base}&page=2",
        f"{amazon_base}&page=3",
    ]

    all_products = []

    def fetch_and_parse(url):
        html = scraper.fetch_page(url)
        return scraper.parse_products(html) if html else []

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fetch_and_parse, url): url for url in urls}
        for future in as_completed(futures):
            batch = future.result()
            for product in batch:
                product["source"] = "Amazon"
            all_products.extend(batch)
            print(f"[stream] Amazon batch: {len(batch)} products")
            for product in batch:
                yield f'data: {json.dumps({"type": "product", "item": product})}\n\n'

    print(f"[stream] Total: {len(all_products)} products")
    cache.set(query, all_products)
    yield f'data: {json.dumps({"type": "done", "total": len(all_products)})}\n\n'
