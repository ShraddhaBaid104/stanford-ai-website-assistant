"""
Production Guardrail Service

Coordinates all guardrails used by the Stanford AI
Website Assistant.
"""

from __future__ import annotations

from typing import List

from app.models import RetrievedDocument

from app.rag.guardrails.domain_guard import DomainGuard
from app.rag.guardrails.prompt_injection import PromptInjectionGuard
from app.rag.guardrails.retrieval_guard import RetrievalGuard
from app.rag.guardrails.context_guard import ContextGuard


class GuardrailService:

    def __init__(self):

        self.domain_guard = DomainGuard()

        self.prompt_guard = PromptInjectionGuard()

        self.retrieval_guard = RetrievalGuard()

        self.context_guard = ContextGuard()

    ####################################################################
    # Before Retrieval
    ####################################################################

    def validate_question(
        self,
        question: str,
    ) -> str | None:
        """
        Returns a fallback response if the
        question should be rejected.

        Returns None if the question is allowed.
        """

        if self.prompt_guard.is_prompt_injection(
                question
        ):
            return self.prompt_guard.fallback_message()

        if not self.domain_guard.is_in_domain(
                question
        ):
            return self.domain_guard.fallback_message()

        return None

    ####################################################################
    # After Retrieval
    ####################################################################

    def validate_documents(
        self,
        documents: List[RetrievedDocument],
    ) -> str | None:
        """
        Validate retrieved Stanford documents.

        Returns None if retrieval quality is acceptable.
        """

        if not self.retrieval_guard.has_sufficient_context(
                documents
        ):
            return self.retrieval_guard.fallback_message()

        if not self.context_guard.has_sufficient_context(
                documents
        ):
            return self.context_guard.fallback_message()

        return None