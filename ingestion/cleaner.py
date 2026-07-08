"""
cleaner.py

Validate and clean crawled Stanford documents before chunking.
"""

from app.core.config import (
    RAW_DATA_FILE,
    CLEAN_DATA_FILE,
)

from ingestion.utils import (
    load_json,
    save_json,
)


MIN_CONTENT_LENGTH = 200


def remove_duplicate_urls(documents):
    """
    Keep only the first occurrence of each URL.
    """

    seen = set()
    cleaned = []

    for doc in documents:

        url = doc["url"]

        if url in seen:
            continue

        seen.add(url)
        cleaned.append(doc)

    return cleaned


def remove_empty_documents(documents):
    """
    Remove pages with no useful text.
    """

    cleaned = []

    for doc in documents:

        text = doc["content"].strip()

        if not text:
            continue

        cleaned.append(doc)

    return cleaned


def remove_short_documents(documents):
    """
    Remove pages with very little content.
    """

    cleaned = []

    for doc in documents:

        if len(doc["content"]) < MIN_CONTENT_LENGTH:
            continue

        cleaned.append(doc)

    return cleaned


def normalize_metadata(documents):
    """
    Normalize title and URL formatting.
    """

    for doc in documents:

        doc["title"] = doc["title"].strip()

        doc["url"] = doc["url"].strip()

    return documents


def clean_documents(documents):
    """
    Run the complete cleaning pipeline.
    """

    documents = remove_duplicate_urls(documents)

    documents = remove_empty_documents(documents)

    documents = remove_short_documents(documents)

    documents = normalize_metadata(documents)

    return documents
def run_cleaner():
    """
    Pipeline entry point.

    Loads the raw crawl output, cleans it,
    saves the cleaned documents and returns them.
    """

    documents = load_json(RAW_DATA_FILE)

    cleaned = clean_documents(documents)

    save_json(
        cleaned,
        CLEAN_DATA_FILE
    )

    return cleaned

def main():

    print("=" * 60)
    print("Stanford Document Cleaner")
    print("=" * 60)

    documents = load_json(RAW_DATA_FILE)

    print(f"Loaded : {len(documents)}")

    cleaned = run_cleaner()

    print(f"Remaining : {len(cleaned)}")

    print()

    print("=" * 60)
    print("Cleaning Complete")
    print("=" * 60)
    print(f"Output : {CLEAN_DATA_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()