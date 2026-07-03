"""
embedder.py

Production embedding pipeline.

Responsibilities
----------------
- Connect to persistent ChromaDB
- Generate OpenAI embeddings
- Detect existing chunks
- Skip unchanged chunks
- Update modified chunks
- Add new chunks
"""

from pathlib import Path

from chromadb import PersistentClient

from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
)

# -------------------------------------------------------------------
# Embedding Model
# -------------------------------------------------------------------

embedding_model = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

# -------------------------------------------------------------------
# Chroma Client
# -------------------------------------------------------------------


def get_chroma_collection():
    """
    Returns the persistent Chroma collection.
    Creates the database if it does not already exist.
    """

    Path(CHROMA_DB_DIR).mkdir(
        parents=True,
        exist_ok=True
    )

    client = PersistentClient(
        path=str(CHROMA_DB_DIR)
    )

    collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME
    )

    return collection

# -------------------------------------------------------------------
# Batch Helper
# -------------------------------------------------------------------


def batch_documents(
    documents: list[Document],
    batch_size: int = 100
):
    """
    Yield documents in batches.
    """

    for i in range(
        0,
        len(documents),
        batch_size
    ):
        yield documents[
            i:i + batch_size
        ]


# -------------------------------------------------------------------
# Embedding Helper
# -------------------------------------------------------------------


def generate_embeddings(
    documents: list[Document]
):
    """
    Generate embeddings for
    a batch of documents.
    """

    texts = [
        doc.page_content
        for doc in documents
    ]

    return embedding_model.embed_documents(
        texts
    )


# -------------------------------------------------------------------
# Statistics
# -------------------------------------------------------------------


class IndexingStats:

    def __init__(self):

        self.total = 0

        self.new = 0

        self.updated = 0

        self.skipped = 0

    def print_summary(self):

        print()

        print("=" * 50)

        print("Indexing Summary")

        print("=" * 50)

        print(
            f"Total Chunks : {self.total}"
        )

        print(
            f"New          : {self.new}"
        )

        print(
            f"Updated      : {self.updated}"
        )

        print(
            f"Skipped      : {self.skipped}"
        )

        print("=" * 50)

        print()
# -------------------------------------------------------------------
# Incremental Indexing
# -------------------------------------------------------------------


def embed_documents(
    documents: list[Document],
    batch_size: int = 100,
):
    """
    Incrementally index documents into ChromaDB.

    New chunks:
        inserted

    Existing unchanged chunks:
        skipped

    Existing modified chunks:
        updated
    """

    collection = get_chroma_collection()

    stats = IndexingStats()

    # Load all existing IDs and hashes once
    existing = collection.get(
        include=["metadatas"]
    )

    existing_chunks = {}

    existing_ids = existing.get("ids", [])
    existing_metadata = existing.get("metadatas", [])

    for chunk_id, metadata in zip(
            existing_ids,
            existing_metadata,
    ):
        existing_chunks[chunk_id] = metadata

    for batch in batch_documents(
        documents,
        batch_size=batch_size,
    ):

        stats.total += len(batch)

        documents_to_embed = []

        embeddings_to_store = []

        ids_to_store = []

        metadatas_to_store = []

        for doc in batch:

            chunk_id = doc.metadata["id"]

            metadata = doc.metadata

            existing_metadata = existing_chunks.get(
                chunk_id
            )

            if existing_metadata is None:

                stats.new += 1

                documents_to_embed.append(doc)

                continue

            existing_hash = existing_metadata.get(
                "content_hash"
            )

            current_hash = metadata.get(
                "content_hash"
            )

            if existing_hash == current_hash:

                stats.skipped += 1

                continue

            stats.updated += 1

            documents_to_embed.append(doc)

        if not documents_to_embed:
            continue

        embeddings = generate_embeddings(
            documents_to_embed
        )

        for doc, embedding in zip(
            documents_to_embed,
            embeddings,
        ):

            ids_to_store.append(
                doc.metadata["id"]
            )

            embeddings_to_store.append(
                embedding
            )

            metadatas_to_store.append(
                doc.metadata
            )

        collection.upsert(
            ids=ids_to_store,
            embeddings=embeddings_to_store,
            documents=[
                doc.page_content
                for doc in documents_to_embed
            ],
            metadatas=metadatas_to_store,
        )
        for metadata in metadatas_to_store:
            existing_chunks[
                metadata["id"]
            ] = metadata

    stats.print_summary()

    return stats


# -------------------------------------------------------------------
# Standalone Execution
# -------------------------------------------------------------------

if __name__ == "__main__":

    from ingestion.chunker import build_chunks

    docs = build_chunks(
        save_debug=True
    )

    embed_documents(docs)