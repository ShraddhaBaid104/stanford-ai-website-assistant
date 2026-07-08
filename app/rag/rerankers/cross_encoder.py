"""
Production Cross Encoder Reranker

Uses a HuggingFace cross encoder to rerank
documents after hybrid retrieval.

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List

from sentence_transformers import CrossEncoder

from app.core.logging import logger
from app.models import RetrievedDocument

from app.rag.rerankers.base import BaseReranker


class CrossEncoderReranker(BaseReranker):
    """
    Reranks retrieved documents using a cross encoder.
    """

    MODEL_NAME = "BAAI/bge-reranker-base"

    def __init__(self):

        logger.info(
            "Loading CrossEncoder reranker."
        )

        self.model = CrossEncoder(
            self.MODEL_NAME
        )

        logger.info(
            "CrossEncoder loaded successfully."
        )

    def rerank(
        self,
        question: str,
        documents: List[RetrievedDocument],
    ) -> List[RetrievedDocument]:

        if not documents:
            return documents

        pairs = [
            (
                question,
                document.content,
            )
            for document in documents
        ]

        scores = self.model.predict(
            pairs
        )

        ranked = sorted(
            zip(documents, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        reranked = []

        for document, score in ranked:

            document.score = float(score)

            reranked.append(document)

        logger.info(
            "Reranked %d documents.",
            len(reranked),
        )

        return reranked