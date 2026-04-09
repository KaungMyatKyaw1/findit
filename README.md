# findit — Amazon Product Search

Flask app that searches Amazon and streams results in real time using Server-Sent Events (up to 20 pages, batched).

**Live Demo:** [https://findit.work](https://findit.work)

## Setup

```bash
git clone https://github.com/KaungMyatKyaw1/findit.git
cd findit
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Deploy

```bash
gcloud run deploy findit-hub --source . --region us-central1 --allow-unauthenticated
```

## Structure

```
app.py        — Flask routes
scraper.py    — Amazon HTML fetching & parsing
stream.py     — SSE generator (20 pages, batches of 5)
cache.py      — In-memory cache (1 hr expiry)
params.py     — Query parameter parsing
templates/bs_search.html — UI
static/css/style.css     — Styles
static/js/stream.js      — SSE client logic
```

## Disclaimer

For **educational purposes only**. Scraping Amazon may violate their [Terms of Use](https://www.amazon.com/gp/help/customer/display.html?nodeId=508088).
