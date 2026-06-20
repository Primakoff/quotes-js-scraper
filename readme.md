# Quotes (JS) Scraper

A web scraper for **JavaScript-rendered** pages, built on the
[quotes.toscrape.com/js](https://quotes.toscrape.com/js/) sandbox — a site
where the content is drawn by JavaScript, so a naive `requests` call returns
an empty page.

Instead of spinning up a heavy headless browser, this scraper uses the
lightweight, robust approach the pros reach for first: the data is already
embedded in the page inside a `<script>` tag (`var data = [...]`), so we
extract that JSON directly. No Selenium, no Playwright.

> A learning / portfolio project demonstrating how to diagnose and fix a
> scraper that "broke" because a site moved to client-side rendering.

## The problem this solves

When a site renders content with JavaScript, the HTML returned by the server
is mostly an empty shell — the data appears only after the browser runs JS.
A scraper written for the old static HTML suddenly finds nothing.

The fix follows a "ladder" from easiest to heaviest:

1. **Hidden JSON API** — check the browser's Network tab (F12) for a request
   that returns the data as JSON, and call it directly.
2. **Embedded JSON** — the data is often baked into the page in a `<script>`
   tag. ← *this project uses this approach*
3. **Updated selectors** — if the site just changed its HTML structure.
4. **Headless browser** (Selenium / Playwright) — only when nothing above works.

## Features

- Extracts the embedded `var data = [...]` JSON from each page
- Follows pagination automatically via the "Next" button
- Retries failed requests, polite delay between pages
- Exports to **CSV** and **JSON**
- Includes a small test (`test_extract.py`) that verifies the parsing logic

## Tech stack

- Python 3.10+
- requests, beautifulsoup4

## Installation

```bash
git clone https://github.com/<your-username>/quotes-js-scraper.git
cd quotes-js-scraper
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python scraper.py                       # all pages -> data/quotes.csv + .json
python scraper.py --format json         # JSON only
python scraper.py --max-pages 3         # first 3 pages (for testing)
```

## Example output

`data/quotes.json`

```json
[
  {
    "text": "The world as we have created it is a process of our thinking.",
    "author": "Albert Einstein",
    "tags": "change; deep-thoughts; thinking; world"
  }
]
```

## Running the test

```bash
python test_extract.py
```

It feeds the parser a small page that mirrors the real site's structure and
checks that quotes, authors, tags and the pagination link are extracted
correctly — without needing a network connection.

## Responsible scraping

quotes.toscrape.com is a sandbox explicitly built for scraping practice. When
adapting these techniques to other sites, always check the target's
`robots.txt` and Terms of Service, keep request rates low, and avoid sites
that prohibit automated access.

## License

MIT