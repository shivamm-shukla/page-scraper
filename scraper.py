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


class PageMiner:

    def __init__(self, raw_address):
        self.target = self._format_address(raw_address)
        self.page_heading = ""
        self.text_block = ""
        self.hyperlinks = []

    def _format_address(self, address):
        if not address.startswith(("http://", "https://")):
            return "https://" + address
        return address

    def _gather_links(self, browser_page):
        discovered = set()
        anchor_nodes = browser_page.query_selector_all("a[href]")

        for node in anchor_nodes:
            ref = node.get_attribute("href")
            if ref:
                absolute_path = urljoin(self.target, ref)
                if absolute_path.startswith(("http://", "https://")):
                    discovered.add(absolute_path)

        return sorted(discovered)

    def execute(self):
        with sync_playwright() as engine:
            chromium = engine.chromium.launch(headless=True)
            tab = chromium.new_page()

            tab.goto(self.target, timeout=60000)
            tab.wait_for_load_state("networkidle")

            # Capture title
            self.page_heading = tab.title().strip()

            # Remove non-visible elements inside browser
            tab.evaluate("""
                () => {
                    document.querySelectorAll('script, style, noscript')
                        .forEach(el => el.remove());
                }
            """)

            # Capture visible body text
            self.text_block = tab.inner_text("body").strip()

            # Capture hyperlinks
            self.hyperlinks = self._gather_links(tab)

            chromium.close()

    def display(self):
        print(self.page_heading)
        print()
        print(self.text_block)
        print()
        for item in self.hyperlinks:
            print(item)


def main():
    if len(sys.argv) != 2:
        print("Usage: python scraper.py <url>")
        sys.exit(1)

    worker = PageMiner(sys.argv[1])

    try:
        worker.execute()
        worker.display()
    except Exception as fault:
        print(f"Runtime Error: {fault}")
        sys.exit(1)


if __name__ == "__main__":
    main()