# Page Scraper

Command-line scraper that fetches one or two web pages, extracts the title, visible body text, all absolute links, and computes a 64-bit SimHash fingerprint for the body text. When two URLs are provided, it also reports how many bits the two fingerprints share in common.

## Features

- Normalizes input URLs by adding `https://` when missing.
- Removes `script` and `style` tags before extracting body text.
- Extracts absolute links using the page as the base URL.
- Computes a 64-bit SimHash over word frequencies in the body.
- Compares two pages by reporting common fingerprint bits.

## Requirements

- Python 3
- `requests`
- `beautifulsoup4`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Scrape a single page:

```bash
python scraper.py https://example.com
```

Scrape and compare two pages:

```bash
python scraper.py https://example.com https://example.org
```

If the URL does not start with `http://` or `https://`, it will be prefixed with `https://`.

## Output Format

For a single URL:

- `TITLE: <page title>`
- `BODY: <visible body text>`
- `SIMHASH: <64-bit binary fingerprint>`
- `LINK: <absolute url>` (one per line)

For two URLs, each field is prefixed with `URL1_` or `URL2_`, followed by a summary line:

- `URL1_TITLE: <page title>`
- `URL1_BODY: <visible body text>`
- `URL1_SIMHASH: <64-bit binary fingerprint>`
- `URL1_LINK: <absolute url>` (one per line)
- `URL2_TITLE: <page title>`
- `URL2_BODY: <visible body text>`
- `URL2_SIMHASH: <64-bit binary fingerprint>`
- `URL2_LINK: <absolute url>` (one per line)
- `COMMON_BITS: <count>`

## Notes

- Network requests use a 10-second timeout and a browser-like user agent.


