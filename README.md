# Page Scraper

This script fetches a web page and prints:
- Title
- Body text
- Simhash of the body (64-bit)
- All links (one per line)

Each line is labeled, for example:
- `TITLE: ...`
- `BODY: ...`
- `SIMHASH: ...`
- `LINK: ...`

If you pass two URLs, it prints results for both and a final line:
- `URL1_TITLE: ...`, `URL1_BODY: ...`, `URL1_SIMHASH: ...`, `URL1_LINK: ...`
- `URL2_TITLE: ...`, `URL2_BODY: ...`, `URL2_SIMHASH: ...`, `URL2_LINK: ...`
- `COMMON_BITS: <count>`


## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python scraper.py https://example.com
```

```bash
python scraper.py https://example.com https://example.org
```
