import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def normalize_url(url):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"https://{url}"


def fetch_html(url):
    agent_name_header = {
        "User-Agent": "Mozilla/5.0"
    }

    page_response = requests.get(url, headers=agent_name_header, timeout = 10)
    if page_response.status_code != 200:
        raise Exception(
            f"Failed to fetch {url}. Status Code: {page_response.status_code}"
        )

    return page_response.text


def extract_title(soup):
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)
    return ""


def extract_body_text(soup):
    for script_or_style in soup.find_all(["script", "style"]):
        script_or_style.decompose()
    body = soup.find("body")
    if body:
        return body.get_text(separator = " ", strip = True)
    else:
        return ""


def extract_links(soup, base_url):
    final_links = set()
    for anchor_tag in soup.find_all("a", href=True):
        link = anchor_tag["href"]
        absolute_url = urljoin(base_url, link)
        if absolute_url.startswith("http://") or absolute_url.startswith("https://"):
            final_links.add(absolute_url)
    return sorted(final_links)


def crawl_page(url):
    normalized_url = normalize_url(url)
    html = fetch_html(normalized_url)
    soup = BeautifulSoup(html, "html.parser")
    page_tittle = extract_title(soup)
    body_text = extract_body_text(soup)
    final_links = extract_links(soup, normalized_url)
    return page_tittle, body_text, final_links


def print_results(page_tittle, body_text, final_links):
    print(page_tittle)
    print(body_text)
    for link in final_links:
        print(f"LINK: {link}")


def main():
    if len(sys.argv) != 2:
        print("Please Enter: python3 scraper.py https://sitare.org.")
        sys.exit(1)

    url = sys.argv[1]
    try:
        page_tittle, body_text, final_links = crawl_page(url)
        print_results(page_tittle, body_text, final_links)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing the page: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
