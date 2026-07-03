"""
parser.py

Utilities for extracting clean text and metadata from HTML pages.
"""

from bs4 import BeautifulSoup


# ---------------------------------------------------------
# Remove Unwanted HTML Elements
# ---------------------------------------------------------

REMOVE_TAGS = [
    "script",
    "style",
    "noscript",
    "svg",
    "iframe"
]

REMOVE_LAYOUT = [
    "header",
    "footer",
    "nav",
    "aside"
]


def clean_html(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Remove unwanted HTML elements.
    """

    for tag in soup(REMOVE_TAGS):
        tag.decompose()

    for tag in soup.find_all(REMOVE_LAYOUT):
        tag.decompose()

    return soup


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extract the page title.
    """

    if soup.title and soup.title.string:

        return soup.title.string.strip()

    return "No Title"


def extract_text(soup: BeautifulSoup) -> str:
    """
    Extract readable text from HTML.
    """

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return text


def normalize_whitespace(text: str) -> str:
    """
    Remove repeated whitespace.
    """

    return " ".join(text.split())


def extract_clean_text(html: str) -> tuple[str, str]:
    """
    Parse HTML and return

    (title, clean_text)
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    soup = clean_html(soup)

    title = extract_title(soup)

    text = extract_text(soup)

    text = normalize_whitespace(text)

    return title, text