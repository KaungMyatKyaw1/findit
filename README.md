# Amazon Product Scraper

A Flask web app that searches Amazon and streams product results (name, price, image, link) to the browser in real time using Server-Sent Events.

## Requirements

- Python 3.10+

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/KaungMyatKyaw1/bs4_scraper.git
cd bs4_scraper

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Project Structure

```
bs4_scraper/
  app.py          — Flask routes
  scraper.py      — Fetching and parsing Amazon HTML
  stream.py       — Server-Sent Events generator
  cache.py        — In-memory result cache (1 hour expiry)
  params.py       — URL query parameter parsing
  templates/
    bs_search.html — UI
```

## Notes

- Results are cached in memory for 1 hour per search query. Restart the server to clear the cache.
- Amazon may block requests from cloud/datacenter IPs. The scraper works best when run locally.

## Disclaimer

This project is for **educational purposes only**. It demonstrates web scraping techniques using Python and BeautifulSoup. Scraping Amazon may violate their [Conditions of Use](https://www.amazon.com/gp/help/customer/display.html?nodeId=508088). Do not use this for commercial purposes or at scale. For production use, use the official [Amazon Product Advertising API](https://affiliate-program.amazon.com/assoc_credentials/home).
