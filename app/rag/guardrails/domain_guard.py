"""
Domain Guard

Determines whether a user's question is related to Stanford University.
"""

from __future__ import annotations


class DomainGuard:

    STANFORD_KEYWORDS = [
        "stanford",
        "admission",
        "apply",
        "application",
        "research",
        "faculty",
        "student",
        "students",
        "course",
        "courses",
        "degree",
        "undergraduate",
        "graduate",
        "campus",
        "tuition",
        "scholarship",
        "financial aid",
        "housing",
        "library",
        "department",
        "professor",
        "engineering",
        "medicine",
        "law",
        "business",
        "education",
        "registrar",
        "academics",
        "university",
    ]

    def is_in_domain(
        self,
        question: str,
    ) -> bool:

        question = question.lower()

        return any(
            keyword in question
            for keyword in self.STANFORD_KEYWORDS
        )

    @staticmethod
    def fallback_message() -> str:

        return (
            "I'm designed to answer questions about "
            "Stanford University and information available "
            "on the Stanford website."
        )