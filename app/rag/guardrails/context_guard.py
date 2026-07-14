"""
Context Guard

Validates that the retrieved context contains enough
useful information before sending it to the LLM.
"""

from __future__ import annotations

from typing import List

from app.models import RetrievedDocument


class ContextGuard:

    def __init__(
        self,
        minimum_characters: int = 300,
    ):
        self.minimum_characters = minimum_characters

    def has_sufficient_context(
        self,
        documents: List[RetrievedDocument],
    ) -> bool:
        """
        Returns True if the retrieved context contains
        enough text to answer the question.
        """

        if not documents:
            return False

        total_characters = sum(
            len(document.content)
            for document in documents
            if document.content
        )

        return total_characters >= self.minimum_characters

    @staticmethod
    def fallback_message() -> str:

        return (
            "I couldn't find enough relevant information "
            "from the Stanford website to answer your question."
        )