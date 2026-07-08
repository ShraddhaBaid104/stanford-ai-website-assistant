"""
Production BM25 Retriever

Responsible for:
- Loading Stanford documents from ChromaDB
- Building a BM25 keyword index
- Returning RetrievedDocument objects

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List

from chromadb import PersistentClient
from rank_bm25 import BM25Okapi

from app.core.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_DB_DIR,
    TOP_K_RESULTS,
)

from app.core.exceptions import RetrieverError
from app.core.logging import logger
from app.models import RetrievedDocument

from app.rag.retrievers.base import BaseRetriever


class BM25Retriever(BaseRetriever):
    """
    BM25 keyword retriever built from the ChromaDB collection.
    """

    def __init__(
        self,
        k: int = TOP_K_RESULTS,
    ):

        logger.info("Initializing BM25Retriever.")

        self.k = k

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

        self.documents = data["documents"]
        self.metadatas = data["metadatas"]

        tokenized_documents = [
            document.lower().split()
            for document in self.documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

        logger.info(
            "BM25Retriever initialized with %d chunks.",
            len(self.documents),
        )

    def retrieve(
        self,
        question: str,
    ) -> List[RetrievedDocument]:
        """
        Retrieve documents using BM25.
        """

        try:

            query_tokens = question.lower().split()

            scores = self.bm25.get_scores(
                query_tokens
            )

            ranked_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True,
            )[: self.k]

            results: List[RetrievedDocument] = []

            for index in ranked_indices:

                metadata = self.metadatas[index]

                results.append(
                    RetrievedDocument(
                        id=metadata["id"],
                        title=metadata.get(
                            "title",
                            "Unknown",
                        ),
                        url=metadata.get(
                            "url",
                            "",
                        ),
                        content=self.documents[index],
                        score=float(scores[index]),
                    )
                )

            return results

        except Exception as exc:

            logger.exception(
                "BM25 retrieval failed."
            )

            raise RetrieverError(
                f"BM25 retrieval failed: {exc}"
            ) from exc