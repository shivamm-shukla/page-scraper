import re
import sys

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def normalize_url(url):
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"https://{url}"


def fetch_html(url, timeout=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_title(soup):
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)
    return ""


def extract_body_text(soup):
    for script in soup(["script", "style"]):
        script.decompose()
    body = soup.find("body")
    target = body if body else soup
    return target.get_text(separator=" ", strip=True)


def extract_links(soup, base_url):
    links = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        absolute_url = urljoin(base_url, href)
        if absolute_url.startswith("http://") or absolute_url.startswith("https://"):
            links.add(absolute_url)
    return sorted(links)


def scrape_page(url):
    normalized_url = normalize_url(url)
    html = fetch_html(normalized_url)
    soup = BeautifulSoup(html, "html.parser")
    title = extract_title(soup)
    body_text = extract_body_text(soup)
    links = extract_links(soup, normalized_url)
    return title, body_text, links


def tokenize_words(text):
    return re.findall(r"[A-Za-z0-9]+", text.lower())


def word_frequencies(text):
    frequencies = {}
    for word in tokenize_words(text):
        frequencies[word] = frequencies.get(word, 0) + 1
    return frequencies


def rolling_hash_64(word, p=53):
    mask = (1 << 64) - 1
    value = 0
    power = 1
    for ch in word:
        value = (value + (ord(ch) * power)) & mask
        power = (power * p) & mask
    return value


def simhash_from_frequencies(frequencies):
    bit_sums = [0] * 64
    for word, weight in frequencies.items():
        h = rolling_hash_64(word)
        for bit_index in range(64):
            bit = (h >> bit_index) & 1
            if bit == 1:
                bit_sums[bit_index] += weight
            else:
                bit_sums[bit_index] -= weight
    fingerprint = 0
    for bit_index, total in enumerate(bit_sums):
        if total > 0:
            fingerprint |= (1 << bit_index)
    return fingerprint


def simhash_for_text(text):
    frequencies = word_frequencies(text)
    return simhash_from_frequencies(frequencies)


def count_common_bits(hash_a, hash_b):
    xor_value = hash_a ^ hash_b
    different_bits = bin(xor_value).count("1")
    return 64 - different_bits


def print_results(title, body_text, links, simhash):
    print(f"TITLE: {title}")
    print(f"BODY: {body_text}")
    print(f"SIMHASH: {simhash:016x}")
    for link in links:
        print(f"LINK: {link}")


def print_results_with_prefix(prefix, title, body_text, links, simhash):
    print(f"{prefix}_TITLE: {title}")
    print(f"{prefix}_BODY: {body_text}")
    print(f"{prefix}_SIMHASH: {simhash:016x}")
    for link in links:
        print(f"{prefix}_LINK: {link}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <URL> [URL2]", file=sys.stderr)
        print("Example: python scraper.py https://example.com", file=sys.stderr)
        print("Example: python scraper.py https://a.com https://b.com", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    second_url = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        title, body_text, links = scrape_page(url)
        simhash = simhash_for_text(body_text)
        if second_url:
            second_title, second_body_text, second_links = scrape_page(second_url)
            second_simhash = simhash_for_text(second_body_text)
            print_results_with_prefix("URL1", title, body_text, links, simhash)
            print_results_with_prefix(
                "URL2", second_title, second_body_text, second_links, second_simhash
            )
            common_bits = count_common_bits(simhash, second_simhash)
            print(f"COMMON_BITS: {common_bits}")
        else:
            print_results(title, body_text, links, simhash)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing the page: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
