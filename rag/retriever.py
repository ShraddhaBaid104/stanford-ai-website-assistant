"""
Production Retrieval Layer

Responsible for:
- Connecting to ChromaDB
- Retrieving relevant Stanford chunks
- Returning LangChain Documents
- Including similarity scores

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List, Tuple

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from config import (
    OPENAI_API_KEY,
    CHROMA_DB_DIR,
    CHROMA_COLLECTION_NAME,
)


class StanfordRetriever:
    """
    Production wrapper around Chroma retrieval.
    """

    def __init__(
        self,
        k: int = 5,
    ):
        self.k = k

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=OPENAI_API_KEY,
        )

        self.vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=CHROMA_DB_DIR,
            embedding_function=embeddings,
        )

    def retrieve(
        self,
        question: str,
    ) -> List[Document]:
        """
        Retrieve top-k relevant documents.
        """

        return self.vectorstore.similarity_search(
            query=question,
            k=self.k,
        )

    def retrieve_with_scores(
            self,
            question: str,
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve documents along with their vector distances.

        Note:
            Lower distance values indicate more relevant results.
        """

        return self.vectorstore.similarity_search_with_score(
            query=question,
            k=self.k,
        )
