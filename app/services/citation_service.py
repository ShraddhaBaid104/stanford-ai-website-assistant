"""
Stores the latest citations for each conversation session.
"""

from app.models import Citation


class CitationService:

    def __init__(self):
        self._cache: dict[str, list[Citation]] = {}

    def save(
        self,
        session_id: str,
        citations: list[Citation],
    ):
        self._cache[session_id] = citations

    def get(
        self,
        session_id: str,
    ) -> list[Citation]:

        return self._cache.get(
            session_id,
            [],
        )