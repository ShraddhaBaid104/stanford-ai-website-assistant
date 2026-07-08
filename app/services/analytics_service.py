"""
Analytics Service

Logs metadata about chatbot requests.

Author: Shraddha Nahata
"""

from __future__ import annotations

import time

from app.core.logging import logger


class AnalyticsService:
    """
    Logs request metadata for monitoring and evaluation.
    """

    def log_request(
        self,
        session_id: str,
        question: str,
        rewritten_question: str,
        retrieved_documents: int,
        model: str,
        elapsed_time: float,
    ) -> None:

        logger.info(
            (
                "Analytics | "
                "session=%s | "
                "question=%s | "
                "rewritten=%s | "
                "documents=%d | "
                "model=%s | "
                "time=%.2fs"
            ),
            session_id,
            question,
            rewritten_question,
            retrieved_documents,
            model,
            elapsed_time,
        )