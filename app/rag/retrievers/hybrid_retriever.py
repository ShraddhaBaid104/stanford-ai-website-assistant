"""
Production Hybrid Retriever

Responsible for:
- Combining Vector Search and BM25 Search
- Performing Reciprocal Rank Fusion (RRF)
- Returning the final ranked Stanford documents

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import Dict, List

from app.core.config import TOP_K_RESULTS
from app.core.exceptions import RetrieverError
from app.core.logging import logger
from app.models import RetrievedDocument

from app.rag.retrievers.base import BaseRetriever
from app.rag.retrievers.bm25_retriever import BM25Retriever
from app.rag.retrievers.stanford_retriever import StanfordRetriever


class HybridRetriever(BaseRetriever):
    """
    Hybrid retrieval using Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        k: int = TOP_K_RESULTS,
        rrf_k: int = 60,
    ):

        logger.info("Initializing HybridRetriever.")

        self.k = k
        self.rrf_k = rrf_k

        self.vector_retriever = StanfordRetriever(k=k)

        self.bm25_retriever = BM25Retriever(k=k)

        logger.info("HybridRetriever initialized successfully.")

    def retrieve(
        self,
        question: str,
    ) -> List[RetrievedDocument]:
        """
        Retrieve documents using both Vector Search and BM25,
        then combine them using Reciprocal Rank Fusion.
        """

        try:

            logger.info("Running vector retrieval.")

            vector_results = self.vector_retriever.retrieve(
                question
            )

            logger.info("Running BM25 retrieval.")

            bm25_results = self.bm25_retriever.retrieve(
                question
            )

            logger.info("Applying Reciprocal Rank Fusion.")

            fused_results = self._reciprocal_rank_fusion(
                vector_results,
                bm25_results,
            )

            logger.info(
                "Hybrid retrieval returned %d documents.",
                len(fused_results),
            )

            return fused_results

        except Exception as exc:

            logger.exception(
                "Hybrid retrieval failed."
            )

            raise RetrieverError(
                f"Hybrid retrieval failed: {exc}"
            ) from exc

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[RetrievedDocument],
        bm25_results: List[RetrievedDocument],
    ) -> List[RetrievedDocument]:
        """
        Combine retrieval rankings using Reciprocal Rank Fusion.

        Formula:

            score += 1 / (rrf_k + rank)
        """

        scores: Dict[str, float] = {}

        documents: Dict[str, RetrievedDocument] = {}

        # -------------------------
        # Vector Search Ranking
        # -------------------------

        for rank, document in enumerate(
            vector_results,
            start=1,
        ):

            score = 1.0 / (
                self.rrf_k + rank
            )

            scores[document.id] = (
                scores.get(document.id, 0.0)
                + score
            )

            documents[document.id] = document

        # -------------------------
        # BM25 Ranking
        # -------------------------

        for rank, document in enumerate(
            bm25_results,
            start=1,
        ):

            score = 1.0 / (
                self.rrf_k + rank
            )

            scores[document.id] = (
                scores.get(document.id, 0.0)
                + score
            )

            # Preserve the first occurrence if already present
            documents.setdefault(
                document.id,
                document,
            )

        ranked_ids = sorted(
            scores,
            key=scores.get,
            reverse=True,
        )

        return [
            documents[doc_id]
            for doc_id in ranked_ids[: self.k]
        ]