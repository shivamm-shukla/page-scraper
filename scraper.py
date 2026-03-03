import sys
from urllib.parse import urljoin

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright module not found.")
    print("Install using:")
    print("pip install playwright")
    print("playwright install")
    sys.exit(1)


class PageScraper:

    def __init__(self, input_address):
        self.target = self.formatWebPageAddress(input_address)
        self.page_heading = ""
        self.body_texts = ""
        self.all_outlinks = []

    def formatWebPageAddress(self, page_address):
        if not page_address.startswith(("http://", "https://")):
            return "https://" + page_address
        return page_address

    def collectAllLinks(self, browser_page):
        visited_links = set()
        anchor_nodes = browser_page.query_selector_all("a[href]")

        for node in anchor_nodes:
            ref = node.get_attribute("href")
            if ref:
                final_path = urljoin(self.target, ref)
                if final_path.startswith(("http://", "https://")):
                    visited_links.add(final_path)

        return sorted(visited_links)

    def startScraping(self):
        with sync_playwright() as engine:
            chromium = engine.chromium.launch(headless=True)
            tab = chromium.new_page()

            tab.goto(self.target, timeout=60000)
            tab.wait_for_load_state("networkidle")

            self.page_heading = tab.title().strip()

            tab.evaluate("""
                () => {
                    document.querySelectorAll('script, style, noscript')
                        .forEach(el => el.remove());
                }
            """)

            self.body_texts = tab.inner_text("body").strip()

            self.all_outlinks = self.collectAllLinks(tab)

            chromium.close()

    def toShowOutput(self):
        print(f"Tittle: {self.page_heading}")
        print(f"Body Texts: {self.body_texts}")
        for i in range(len(self.all_outlinks)):
            print(f"{i + 1}: {self.all_outlinks[i]}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python scraper.py <url>")
        sys.exit(1)

    scraprObj = PageScraper(sys.argv[1])

    try:
        scraprObj.startScraping()
        scraprObj.toShowOutput()
    except Exception as error:
        print(f"Runtime Error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()