"""
app.py — Flask entry point. Routes only — no logic lives here.

Each route reads like a plain English description of what happens:
  1. Parse the request parameters
  2. Check the cache
  3. Sort and paginate (or set loading flag)
  4. Render the response

Implementation details live in:
  scraper.py  — fetching, parsing, sorting, pagination
  cache.py    — in-memory result cache with expiry
  stream.py   — Server-Sent Events generator
  params.py   — URL query-string parameter parsing
"""

import os

from flask import Flask, Response, request, render_template, stream_with_context

import scraper
import cache
import stream
import params


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")


@app.route("/", methods=["GET"])
def index():
    query, page, per_page, sort, order = params.parse_search_params(request)

    search_url = scraper.BASE_URL
    loading = False
    page_products = []
    total_items = 0
    total_pages = 1

    if query:
        search_url = scraper.build_search_url(query)
        products = cache.get(query)

        if products is None:
            loading = True  # No cache — skeleton cards shown; SSE fills them in
        else:
            products = scraper.sort_products(products, sort, order)
            page_products, total_items, total_pages, page = scraper.paginate(products, page, per_page)

    return render_template(
        "bs_search.html",
        query=query,
        search_url=search_url,
        loading=loading,
        page_products=page_products,
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        per_page=per_page,
        sort=sort,
        order=order,
        base_url=scraper.BASE_URL,
    )


@app.route("/stream")
def stream_results():
    query = request.args.get("search", "").strip()

    if not query:
        return Response(stream.empty_response(), mimetype="text/event-stream")

    cached = cache.get(query)

    return Response(
        stream_with_context(stream.generate(query, cached)),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    app.run(debug=True)
