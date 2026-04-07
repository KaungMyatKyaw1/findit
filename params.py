"""
params.py — Parses and validates URL query-string parameters.

One function:
  parse_search_params(request)  — returns (query, page, per_page, sort, order)
"""


def parse_search_params(request) -> tuple:
    """Extract and validate search controls from a Flask request object.

    Returns:
        query    — the search string (empty string if none)
        page     — current page number (integer >= 1)
        per_page — items per page (10, 20, or 30; defaults to 20)
        sort     — sort field ("name", "title", "price", or "" for none)
        order    — sort direction ("asc" or "desc"; defaults to "asc")
    """
    query = request.args.get("search", "").strip()

    try:
        page = max(1, int(request.args.get("page", "1")))
    except ValueError:
        page = 1

    try:
        per_page = int(request.args.get("per_page", "20"))
        if per_page not in (10, 20, 30):
            per_page = 20
    except ValueError:
        per_page = 20

    sort = request.args.get("sort", "").strip()
    if sort not in ("name", "title", "price"):
        sort = ""

    order = request.args.get("order", "asc").strip()
    if order not in ("asc", "desc"):
        order = "asc"

    return query, page, per_page, sort, order
