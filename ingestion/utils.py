"""
utils.py

Shared utility functions used throughout the Stanford AI Assistant
project.

Responsibilities
----------------
- JSON file handling
- URL normalization
- Stanford URL validation
- Hash generation
- Chunk ID generation
"""

import hashlib
import json
from pathlib import Path
from urllib.parse import urldefrag, urlparse
from app.core.config import ALLOWED_DOMAINS

# ==========================================================
# JSON Utilities
# ==========================================================
def save_json(data, filepath):
    """
    Save Python data as formatted JSON.
    """

    filepath = Path(filepath)

    filepath.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        filepath,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

def load_json(filepath):
    """
    Load JSON data from disk.
    """

    filepath = Path(filepath)

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ==========================================================
# URL Utilities
# ==========================================================

def normalize_url(url: str) -> str:
    """
    Remove URL fragments.

    Example

    https://abc.com/page#section

    becomes

    https://abc.com/page
    """

    clean_url, _ = urldefrag(url)

    return clean_url.rstrip("/")


def is_stanford_url(url: str) -> bool:
    """
    Check whether a URL belongs to one of the allowed Stanford domains.
    """

    parsed = urlparse(url)

    return parsed.netloc.endswith(tuple(ALLOWED_DOMAINS))

# ==========================================================
# Hash Utilities
# ==========================================================

def generate_document_id(url: str) -> str:
    """
    Generate a stable ID for a webpage.

    Since URLs are unique,
    hashing the URL produces a stable document ID.
    """

    return hashlib.sha256(
        url.encode("utf-8")
    ).hexdigest()


def generate_content_hash(text: str) -> str:
    """
    Generate a SHA256 hash for chunk content.

    Used to detect content changes.
    """

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# ==========================================================
# Chunk Utilities
# ==========================================================

def generate_chunk_id(
    document_id: str,
    chunk_number: int
) -> str:
    """
    Generate a stable chunk ID.

    Example

    document_id:
        a82bd8...

    chunk_number:
        4

    Result:

    a82bd8..._4
    """

    return f"{document_id}_{chunk_number:04d}"