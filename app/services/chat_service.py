"""
Production Chat Service

Coordinates requests between the API layer and the chatbot.
"""

from __future__ import annotations

from app.models import ChatResponse
from app.rag import StanfordChatbot
from app.services.citation_service import citation_service


class ChatService:

    def __init__(self):

        self.chatbot = StanfordChatbot()

    def ask(
        self,
        session_id: str,
        question: str,
    ) -> ChatResponse:

        return self.chatbot.ask(
            session_id=session_id,
            question=question,
        )

    def stream(
        self,
        session_id: str,
        question: str,
    ):

        return self.chatbot.stream(
            session_id=session_id,
            question=question,
        )

    def get_last_citations(
            self,
            session_id: str,
    ):
        return citation_service.get(session_id)
