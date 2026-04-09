# findit — Amazon Product Search

A Flask web app that searches Amazon and streams product results (name, price, image, link) to the browser in real time using Server-Sent Events. Fetches up to 20 pages of results in parallel batches.

## Live Demo

[https://findit.work](https://findit.work)

## Requirements

- Python 3.10+
- Docker (for Cloud Run deployment)

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/KaungMyatKyaw1/findit.git
cd findit

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

## Run locally

```bash
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Deploy to Google Cloud Run

```bash
gcloud run deploy findit-hub --source . --region us-central1 --allow-unauthenticated
```

## Project Structure

```
findit/
  app.py               — Flask routes
  scraper.py           — Fetching and parsing Amazon HTML
  stream.py            — SSE generator (up to 20 pages, batches of 5)
  cache.py             — In-memory result cache (1 hour expiry)
  params.py            — URL query parameter parsing
  requirements.txt     — Python dependencies
  Dockerfile           — Container config for Cloud Run
  templates/
    bs_search.html     — UI template
  static/
    css/style.css      — Styles
    js/stream.js       — SSE client logic
    js/cached.js       — Fallback for cached results
```

## Notes

- Results are cached in memory for 1 hour per search query. Restart the server to clear the cache.
- The scraper works on Google Cloud Run — Google Cloud IPs are not blocked by Amazon at this time.

## Disclaimer

This project is for **educational purposes only**. It demonstrates web scraping techniques using Python and BeautifulSoup. Scraping Amazon may violate their [Conditions of Use](https://www.amazon.com/gp/help/customer/display.html?nodeId=508088). For production use, use the official [Amazon Product Advertising API](https://affiliate-program.amazon.com/assoc_credentials/home).
