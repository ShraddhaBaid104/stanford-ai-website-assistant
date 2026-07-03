"""
crawler.py

Production-ready Stanford website crawler.

Responsibilities
----------------
1. Crawl Stanford webpages.
2. Discover internal links.
3. Extract clean text.
4. Save raw documents.
"""

import time
from collections import deque
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from config import (
    START_URL,
    MAX_PAGES,
    PAGE_TIMEOUT,
    CRAWL_DELAY,
    HEADLESS,
    RAW_DATA_FILE,
)

from ingestion.parser import extract_clean_text

from ingestion.utils import (
    normalize_url,
    is_stanford_url,
    save_json,
)


# ---------------------------------------------------------
# Link Discovery
# ---------------------------------------------------------

def discover_links(soup: BeautifulSoup, current_url: str) -> list[str]:
    """
    Extract Stanford links from the current page.
    """

    links = []

    for tag in soup.find_all("a", href=True):

        href = tag["href"]

        full_url = normalize_url(
            urljoin(current_url, href)
        )

        if not is_stanford_url(full_url):
            continue

        links.append(full_url)

    return links


# ---------------------------------------------------------
# Crawl
# ---------------------------------------------------------

def crawl_website(
    start_url: str = START_URL,
    max_pages: int = MAX_PAGES,
):
    visited = set()

    queue = deque(
        [normalize_url(start_url)]
    )

    documents = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=HEADLESS
        )

        context = browser.new_context()

        page = context.new_page()

        while queue and len(visited) < max_pages:

            current_url = normalize_url(
                queue.popleft()
            )

            if current_url in visited:
                continue

            visited.add(current_url)

            print(
                f"[{len(visited)}/{max_pages}] {current_url}"
            )

            try:

                page.goto(
                    current_url,
                    wait_until="load",
                    timeout=PAGE_TIMEOUT
                )

                page.wait_for_timeout(2000)

            except Exception as e:

                print(f"Failed: {current_url}")

                print(e)

                continue

            html = page.content()

            title, text = extract_clean_text(
                html
            )

            documents.append(

                {

                    "url": current_url,

                    "title": title,

                    "content": text

                }

            )

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            links = discover_links(
                soup,
                current_url
            )

            for link in links:

                if link not in visited:

                    queue.append(link)

            time.sleep(CRAWL_DELAY)

        browser.close()

    save_json(
        documents,
        RAW_DATA_FILE
    )

    return documents


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    print("=" * 60)
    print("Stanford Website Crawler")
    print("=" * 60)

    documents = crawl_website(
        START_URL,
        MAX_PAGES
    )

    print()

    print("=" * 60)
    print("Crawling Complete")
    print("=" * 60)

    print(f"Pages Crawled : {len(documents)}")

    print(f"Output File   : {RAW_DATA_FILE}")

    print("=" * 60)


# ---------------------------------------------------------

if __name__ == "__main__":

    main()