"""scraper.py — Fetches, parses, sorts and paginates Amazon search results.

Functions:
  fetch_page(url)                   — downloads a URL and returns raw HTML
  parse_products(html)              — extracts product cards from HTML
  build_search_url(query)           — builds an Amazon search URL
  sort_products(products, sort, order) — returns a sorted copy of a product list
  paginate(products, page, per_page)— slices a product list for one page
"""

import re
import time
import random
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.amazon.com"

# Browser-like headers so sites don't block the request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}


def fetch_page(url: str) -> str | None:
    """Download a URL and return the HTML string, or None on failure.

    A small random delay is added before each request so sites are
    less likely to detect automated traffic.
    """
    time.sleep(random.uniform(1, 3))
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        print(f"[scraper] {response.status_code} {url}")
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[scraper] FAILED {url}: {e}")
        return None


def parse_products(html: str) -> list[dict]:
    """Extract product information from one Amazon search results page.

    Returns a list of dicts, each with keys: name, title, price, link.

    Amazon uses two different HTML layouts depending on the category,
    so we try the most common one first and fall back to the other.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Primary selector: data-component-type is stable across Amazon layout changes.
    # Fall back to class-based selectors for older / cached HTML.
    product_cards = (
        soup.find_all("div", attrs={"data-component-type": "s-search-result"})
        or soup.find_all("div", class_="sg-col-20-of-24 s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col s-widget-spacing-small sg-col-12-of-16")
        or soup.find_all("div", class_="sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20")
    )

    products = []
    for card in product_cards:
        # Brand / seller name (small text above the title)
        name_tag = (
            card.find(class_="a-size-mini s-line-clamp-1")
            or card.find(class_="a-size-base-plus a-color-base")
            or card.find("span", attrs={"data-hook": "retail-offer-name"})
        )

        # Product title — two possible class names across layouts
        title_tag = (
            card.find(class_="a-size-medium a-spacing-none a-color-base a-text-normal")
            or card.find(class_="a-size-base-plus a-spacing-none a-color-base a-text-normal")
        )

        # Price is hidden in an off-screen span for screen readers
        price_tag = card.find(class_="a-offscreen")

        # Product link — two possible class names across layouts
        link_tag = (
            card.find("a", class_="a-link-normal s-line-clamp-2 puis-line-clamp-3-for-col-4-and-8 s-link-style a-text-normal")
            or card.find("a", class_="a-link-normal s-no-outline")
        )

        # Product image — consistent class across both layouts
        img_tag = card.find("img", class_="s-image")

        products.append({
            "name":  name_tag.get_text(strip=True)  if name_tag  else None,
            "title": title_tag.get_text(strip=True) if title_tag else None,
            "price": price_tag.get_text(strip=True) if price_tag else None,
            "link":  link_tag.get("href")           if link_tag  else None,
            "image": img_tag.get("src")             if img_tag   else None,
        })

    return products


def build_search_url(query: str, base_url: str = BASE_URL) -> str:
    """Build an Amazon search URL for the given query string."""
    return f"{base_url}/s?k={quote_plus(query)}"


def sort_products(products: list, sort: str, order: str = "asc") -> list:
    """Return a sorted copy of products by name, title, or price.

    sort=""      → original order (no sort)
    sort="name"  → alphabetical by brand name
    sort="title" → alphabetical by product title
    sort="price" → numeric price (items with no price go last)
    order="asc"  → ascending (default)
    order="desc" → descending
    """
    reverse = (order == "desc")
    if sort == "price":
        def price_key(item):
            val = item.get("price") or ""
            match = re.search(r"[\d,]+\.?\d*", val)
            return float(match.group().replace(",", "")) if match else float("inf")
        return sorted(products, key=price_key, reverse=reverse)
    if sort in ("name", "title"):
        return sorted(products, key=lambda item: item.get(sort) or "", reverse=reverse)
    return list(products)


def paginate(products: list, page: int, per_page: int) -> tuple:
    """Slice a product list to return only the requested page.

    Returns:
        page_products — the products for this page
        total_items   — total number of products across all pages
        total_pages   — total number of pages
        page          — the actual page served (clamped to valid range)
    """
    total_items = len(products)
    total_pages = max(1, (total_items + per_page - 1) // per_page)
    page = min(page, total_pages)
    start = (page - 1) * per_page
    return products[start : start + per_page], total_items, total_pages, page
