"""
API client for the Stanford AI Website Assistant.
"""

import requests

from config import API_URL


def ask_question(session_id: str, question: str):

    response = requests.post(
        f"{API_URL}/chat",
        json={
            "session_id": session_id,
            "question": question,
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def stream_answer(session_id: str, question: str):

    response = requests.post(
        f"{API_URL}/chat/stream",
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


def get_citations(session_id: str):

    response = requests.get(
        f"{API_URL}/chat/last-citations",
        params={
            "session_id": session_id,
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()