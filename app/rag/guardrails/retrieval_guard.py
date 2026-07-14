"""
Retrieval Confidence Guard

Determines whether the retrieved documents provide
enough confidence to answer the user's question.
"""

from __future__ import annotations

from typing import List

from app.models import RetrievedDocument


class RetrievalGuard:

    def __init__(
        self,
        minimum_score: float = 0.25,
        minimum_documents: int = 2,
    ):
        self.minimum_score = minimum_score
        self.minimum_documents = minimum_documents

    def has_sufficient_context(
        self,
        documents: List[RetrievedDocument],
    ) -> bool:
        """
        Decide whether the retrieved documents are
        strong enough to generate an answer.
        """

        if len(documents) < self.minimum_documents:
            return False

        average_score = (
            sum(doc.score for doc in documents)
            / len(documents)
        )

        return average_score >= self.minimum_score

    @staticmethod
    def fallback_message() -> str:
        return (
            "I couldn't find enough reliable information "
            "from the Stanford website to answer that question. "
            "Please try rephrasing your question or ask about another "
            "Stanford topic."
        )