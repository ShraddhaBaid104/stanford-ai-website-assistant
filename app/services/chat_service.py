"""
Production Chat Service

Coordinates requests between the API layer and the chatbot.
"""

from __future__ import annotations

from app.rag import StanfordChatbot
from app.models import ChatResponse
from app.services import citation_service


class ChatService:
    """
    Service layer for chatbot interactions.
    """

    def __init__(self):

        self.chatbot = StanfordChatbot()

    def ask(
        self,
        session_id: str,
        question: str,
    ) -> ChatResponse:
        """
        Execute a standard (non-streaming) chat request.
        """

        return self.chatbot.ask(
            session_id=session_id,
            question=question,
        )

    def stream(
        self,
        session_id: str,
        question: str,
    ):
        """
        Execute a streaming chat request.
        """

        return self.chatbot.stream(
            session_id=session_id,
            question=question,
        )

    def get_last_citations(
            self,
            session_id: str,
    ):
        return citation_service.get(session_id)