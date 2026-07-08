"""
API client for communicating with the Stanford AI Assistant backend.

Author: Shraddha Nahata
"""

from __future__ import annotations

import requests


BACKEND_URL = "http://localhost:8000"


class StanfordAPI:
    """
    Wrapper around the FastAPI backend.
    """

    def __init__(self):
        self.base_url = BACKEND_URL

    def chat(
        self,
        session_id: str,
        question: str,
    ) -> dict:

        response = requests.post(
            f"{self.base_url}/chat",
            json={
                "session_id": session_id,
                "question": question,
            },
            timeout=120,
        )

        response.raise_for_status()

        return response.json()

    def stream(
        self,
        session_id: str,
        question: str,
    ):

        response = requests.post(
            f"{self.base_url}/chat/stream",
            json={
                "session_id": session_id,
                "question": question,
            },
            stream=True,
            timeout=120,
        )

        response.raise_for_status()

        for chunk in response.iter_content(
                chunk_size=None,
                decode_unicode=True,
        ):
            if chunk:
                yield chunk