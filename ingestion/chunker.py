"""
Production Chunk Builder

Responsibilities
----------------
- Load cleaned documents
- Convert them to LangChain Documents
- Split using RecursiveCharacterTextSplitter
- Enrich every chunk with stable metadata
- Return LangChain Documents
- Optionally save chunk JSON for debugging
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CLEANED_DOCUMENTS_FILE,
    CHUNKED_DOCUMENTS_FILE,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)

from ingestion.utils import (
    load_json,
    save_json,
    generate_document_id,
    generate_chunk_id,
    generate_content_hash,
)


# ------------------------------------------------------------------
# Text Splitter
# ------------------------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)


# ------------------------------------------------------------------
# Build LangChain Documents
# ------------------------------------------------------------------

def create_documents(cleaned_documents: list[dict]) -> list[Document]:
    """
    Convert cleaned JSON documents into LangChain Documents.
    """

    documents = []

    for item in cleaned_documents:
        documents.append(
            Document(
                page_content=item["content"],
                metadata={
                    "url": item["url"],
                    "title": item.get("title", ""),
                },
            )
        )

    return documents


# ------------------------------------------------------------------
# Split Documents
# ------------------------------------------------------------------

def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into overlapping chunks.
    """

    return text_splitter.split_documents(documents)


# ------------------------------------------------------------------
# Add Stable Metadata
# ------------------------------------------------------------------

def enrich_documents(chunks: list[Document]) -> list[Document]:
    """
    Add production metadata to every chunk.
    """

    enriched = []

    chunk_counters = {}

    for chunk in chunks:

        url = chunk.metadata["url"]

        title = chunk.metadata.get("title", "")

        document_id = generate_document_id(url)

        chunk_number = chunk_counters.get(document_id, 0)

        chunk_counters[document_id] = chunk_number + 1

        content_hash = generate_content_hash(chunk.page_content)

        chunk_id = generate_chunk_id(
            document_id=document_id,
            chunk_number=chunk_number,
        )

        chunk.metadata = {
            "id": chunk_id,
            "document_id": document_id,
            "chunk_number": chunk_number,
            "content_hash": content_hash,
            "url": url,
            "title": title,
            "source": url,
        }

        enriched.append(chunk)

    return enriched


# ------------------------------------------------------------------
# Debug Export
# ------------------------------------------------------------------

def export_debug_json(chunks: list[Document]) -> None:
    """
    Save chunks to JSON for inspection/debugging.
    """

    debug_output = []

    for chunk in chunks:

        debug_output.append(
            {
                "page_content": chunk.page_content,
                "metadata": chunk.metadata,
            }
        )

    save_json(
        debug_output,
        CHUNKED_DOCUMENTS_FILE,
    )


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------

def build_chunks(save_debug: bool = True) -> list[Document]:
    """
    Complete chunk-building pipeline.

    Returns:
        List[Document]
    """

    cleaned_documents = load_json(CLEANED_DOCUMENTS_FILE)

    documents = create_documents(cleaned_documents)

    chunks = split_documents(documents)

    chunks = enrich_documents(chunks)

    if save_debug:
        export_debug_json(chunks)

    print(f"Created {len(chunks)} chunks.")

    return chunks


# ------------------------------------------------------------------
# Standalone Execution
# ------------------------------------------------------------------

if __name__ == "__main__":
    build_chunks()