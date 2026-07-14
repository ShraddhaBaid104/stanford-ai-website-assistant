"""
Production Analytics Service

Tracks usage statistics and evaluation metrics.

Author: Shraddha Nahata
"""

from __future__ import annotations

from collections import Counter

from app.models import EvaluationResult


class AnalyticsService:

    def __init__(self):

        self.total_requests = 0

        self.cached_requests = 0

        self.questions = Counter()

        self.evaluations: list[EvaluationResult] = []

    # --------------------------------------------------

    def record_request(
        self,
        cached: bool = False,
    ):

        self.total_requests += 1

        if cached:
            self.cached_requests += 1

    # --------------------------------------------------

    def record_question(
        self,
        question: str,
    ):

        self.questions[question] += 1

    # --------------------------------------------------

    def record_evaluation(
        self,
        evaluation: EvaluationResult,
    ):

        self.evaluations.append(
            evaluation
        )

    # --------------------------------------------------

    def summary(self):

        cache_rate = 0

        if self.total_requests:

            cache_rate = (
                self.cached_requests
                / self.total_requests
            ) * 100

        if not self.evaluations:

            return {

                "total_requests": self.total_requests,

                "cached_requests": self.cached_requests,

                "cache_hit_rate": round(
                    cache_rate,
                    2,
                ),

                "top_questions": self.questions.most_common(
                    10
                ),

                "average_total_time": 0,

                "average_retrieval_time": 0,

                "average_llm_time": 0,

                "average_documents": 0,

                "average_citations": 0,

                "average_answer_words": 0,

                "success_rate": 0,
            }

        n = len(
            self.evaluations
        )

        successful = sum(
            e.passed
            for e in self.evaluations
        )

        return {

            "total_requests": self.total_requests,

            "cached_requests": self.cached_requests,

            "cache_hit_rate": round(
                cache_rate,
                2,
            ),

            "top_questions": self.questions.most_common(
                10
            ),

            "average_total_time": round(
                sum(
                    e.total_time
                    for e in self.evaluations
                ) / n,
                3,
            ),

            "average_retrieval_time": round(
                sum(
                    e.retrieval_time
                    for e in self.evaluations
                ) / n,
                3,
            ),

            "average_llm_time": round(
                sum(
                    e.llm_time
                    for e in self.evaluations
                ) / n,
                3,
            ),

            "average_documents": round(
                sum(
                    e.retrieved_documents
                    for e in self.evaluations
                ) / n,
                2,
            ),

            "average_citations": round(
                sum(
                    e.citation_count
                    for e in self.evaluations
                ) / n,
                2,
            ),

            "average_answer_words": round(
                sum(
                    e.answer_words
                    for e in self.evaluations
                ) / n,
                2,
            ),

            "success_rate": round(
                successful / n * 100,
                2,
            ),
        }


analytics_service = AnalyticsService()