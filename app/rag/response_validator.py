"""
Production Response Validator

Performs lightweight validation on generated responses.

Author: Shraddha Nahata
"""

from __future__ import annotations

from app.core.logging import logger


class ResponseValidator:
    """
    Performs simple validation of generated answers.
    """

    def validate(
        self,
        answer: str,
    ) -> str:
        """
        Validate the generated answer.
        """

        logger.info("Validating generated response.")

        cleaned = answer.strip()

        if not cleaned:
            return (
                "I couldn't find that information in the Stanford website content provided."
            )

        return cleaned