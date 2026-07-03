"""
pipeline.py

Production indexing pipeline.
"""

from ingestion.crawler import crawl_website
from ingestion.cleaner import run_cleaner
from ingestion.chunker import build_chunks
from ingestion.embedder import embed_documents


def run_pipeline():

    print("=" * 60)
    print("Stanford AI Assistant Indexing Pipeline")
    print("=" * 60)

    print("\n[1/4] Crawling website...")
    crawl_website()

    print("\n[2/4] Cleaning documents...")
    run_cleaner()

    print("\n[3/4] Building chunks...")
    documents = build_chunks(save_debug=True)

    print("\n[4/4] Generating embeddings...")
    stats = embed_documents(documents)

    print("\nPipeline completed successfully.")

    return stats


if __name__ == "__main__":
    run_pipeline()