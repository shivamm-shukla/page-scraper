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


def build_word_weight_map(input_text):
    text = input_text.lower()
    words_with_weights = {}

    current_word = ""
    inside_word = False

    for ch in text:
        if ch.isalnum():
            if not inside_word:
                inside_word = True
                current_word = ch
            else:
                current_word += ch
        else:
            if inside_word:
                words_with_weights[current_word] = words_with_weights.get(current_word, 0) + 1
                current_word = ""
                inside_word = False
    
    # for the last word
    if inside_word:
        words_with_weights[current_word] = words_with_weights.get(current_word, 0) + 1

    return words_with_weights



def rolling_hash_64(word, p=53):
    mask = (1 << 64) - 1
    value = 0
    power = 1
    for ch in word:
        value = (value + (ord(ch) * power)) & mask
        power = (power * p) & mask
    return value


def compute_weighted_bit_fingerprint(word_weight_map, fingerprint_length=64):

    bit_contribution_totals = [0] * fingerprint_length

    for word in word_weight_map:

        word_weight = word_weight_map[word]
        hashed_value = rolling_hash_64(word)

        for position in range(fingerprint_length):

            extracted_bit = (hashed_value >> position) & 1

            if extracted_bit == 1:
                bit_contribution_totals[position] += word_weight
            else:
                bit_contribution_totals[position] -= word_weight

    fingerprint_result = 0

    for position in range(fingerprint_length):
        if bit_contribution_totals[position] > 0:
            fingerprint_result |= (1 << position)

    return fingerprint_result

    

def simhash_for_text(text):
    word_weight_map = build_word_weight_map(text)
    return compute_weighted_bit_fingerprint(word_weight_map)


def find_common_bits(fingerprint_a, fingerprint_b):
    xor_value = fingerprint_a ^ fingerprint_b
    different_bits = bin(xor_value).count("1")
    return 64 - different_bits


def print_results(page_tittle, body_text, final_links, simhash):
    print(f"TITLE: {page_tittle}")
    print(f"BODY: {body_text}")
    print(f"SIMHASH: {simhash:064b}")
    for link in final_links:
        print(f"LINK: {link}")


def print_results_with_prefix(prefix, page_tittle, body_text, final_links, simhash):
    print(f"{prefix}_TITLE: {page_tittle}")
    print(f"{prefix}_BODY: {body_text}")
    print(f"{prefix}_SIMHASH: {simhash:064b}")
    for link in final_links:
        print(f"{prefix}_LINK: {link}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <URL1> <URL2>")
        print("Example: python scraper.py https://sitare.org.")
        print("Example: python scraper.py https://sitare.org https://example.com")
        sys.exit(1)

    url = sys.argv[1]
    second_url = sys.argv[2] if len(sys.argv) > 2 else None
    try:
        page_tittle, body_text, final_links = crawl_page(url)
        simhash = simhash_for_text(body_text)
        if second_url:
            second_title, second_body_text, second_links = crawl_page(second_url)
            second_simhash = simhash_for_text(second_body_text)
            print_results_with_prefix("URL1", page_tittle, body_text, final_links, simhash)
            print_results_with_prefix(
                "URL2", second_title, second_body_text, second_links, second_simhash
            )
            common_bits = find_common_bits(simhash, second_simhash)
            print()
            print(f"COMMON_BITS: {common_bits}")
        else:
            print_results(page_tittle, body_text, final_links, simhash)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error parsing the page: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
