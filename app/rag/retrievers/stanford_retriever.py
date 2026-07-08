"""
Production Stanford Retriever

Responsible for:
- Connecting to ChromaDB
- Performing vector search
- Converting LangChain Documents into domain models

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    TOP_K_RESULTS,
)

from app.core.exceptions import RetrieverError
from app.core.logging import logger

from app.models import RetrievedDocument

from app.rag.retrievers.base import BaseRetriever


class StanfordRetriever(BaseRetriever):
    """
    Production wrapper around ChromaDB retrieval.
    """

    def __init__(
        self,
        k: int = TOP_K_RESULTS,
    ):

        logger.info("Initializing StanfordRetriever.")

        self.k = k

        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=OPENAI_API_KEY,
        )

        self.vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            persist_directory=str(CHROMA_DB_DIR),
            embedding_function=self.embeddings,
        )

        logger.info("StanfordRetriever initialized successfully.")

    def retrieve(
        self,
        question: str,
    ) -> List[RetrievedDocument]:
        """
        Retrieve top-k relevant Stanford documents.
        """

        try:

            results = self.vectorstore.similarity_search_with_score(
                query=question,
                k=self.k,
            )

            documents = [
                self._to_retrieved_document(doc, score)
                for doc, score in results
            ]

            return documents

        except Exception as exc:

            logger.exception("Document retrieval failed.")

            raise RetrieverError(
                f"Failed to retrieve documents: {exc}"
            ) from exc

    @staticmethod
    def _to_retrieved_document(
        doc,
        score: float,
    ) -> RetrievedDocument:
        """
        Convert a LangChain Document into the application's
        internal RetrievedDocument model.
        """

        return RetrievedDocument(
            id=doc.metadata.get(
                "document_id",
                doc.metadata.get("url", ""),
            ),
            title=doc.metadata.get("title", "Unknown"),
            url=doc.metadata.get("url", ""),
            content=doc.page_content,
            score=float(score),
        )