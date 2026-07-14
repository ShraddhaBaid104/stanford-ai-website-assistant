"""
Production Evaluation Service

Evaluates every generated response.

Author: Shraddha Nahata
"""

from __future__ import annotations

from app.models import EvaluationResult


class EvaluationService:

    def evaluate(
        self,
        *,
        retrieval_time: float,
        llm_time: float,
        total_time: float,
        documents: list,
        answer: str,
        response_cache_hit: bool,
        semantic_cache_hit: bool,
    ) -> EvaluationResult:
        """
        Evaluate one RAG response.
        """

        scores = [
            d.score
            for d in documents
            if d.score is not None
        ]

        citation_count = len(
            {
                d.url
                for d in documents
                if d.url
            }
        )

        return EvaluationResult(

            retrieval_time=retrieval_time,

            llm_time=llm_time,

            total_time=total_time,

            retrieved_documents=len(documents),

            citation_count=citation_count,

            average_retrieval_score=(
                sum(scores) / len(scores)
                if scores
                else 0.0
            ),

            best_retrieval_score=(
                max(scores)
                if scores
                else 0.0
            ),

            answer_words=len(answer.split()),

            answer_characters=len(answer),

            response_cache_hit=response_cache_hit,

            semantic_cache_hit=semantic_cache_hit,

            passed=(
                len(answer) > 0
                and len(documents) > 0
            ),
        )