"""
inspect_chromadb.py

Utility script for inspecting the ChromaDB vector store.
"""

from chromadb import PersistentClient

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DB_DIR,
)


def inspect_collection():

    client = PersistentClient(
        path=str(CHROMA_DB_DIR)
    )

    collection = client.get_collection(
        CHROMA_COLLECTION_NAME
    )

    data = collection.get(
        include=[
            "documents",
            "metadatas",
        ]
    )

    ids = data.get("ids", [])
    documents = data.get("documents", [])
    metadatas = data.get("metadatas", [])

    print("=" * 70)
    print("ChromaDB Inspection")
    print("=" * 70)

    print(f"Collection : {CHROMA_COLLECTION_NAME}")
    print(f"Total Chunks : {len(ids)}")

    if not ids:

        print("\nDatabase is empty.")

        return

    print("\nSample Chunk")
    print("-" * 70)

    print(f"Chunk ID : {ids[0]}")

    print("\nMetadata")

    for key, value in metadatas[0].items():

        print(f"{key}: {value}")

    print("\nPreview")

    preview = documents[0][:500]

    print(preview)

    print()

    print("=" * 70)


if __name__ == "__main__":

    inspect_collection()