"""
Production Stanford Website Chatbot

Thin wrapper around the ConversationEngine.

Author: Shraddha Nahata
"""

from __future__ import annotations

from app.core.config import TOP_K_RESULTS
from app.core.logging import logger
from app.models import ChatResponse

from app.rag.conversation_engine import ConversationEngine


class StanfordChatbot:
    """
    Public chatbot interface.
    """

    def __init__(
        self,
        k: int = TOP_K_RESULTS,
    ):

        logger.info("Initializing StanfordChatbot.")

        self.engine = ConversationEngine(k=k)

        logger.info("StanfordChatbot initialized successfully.")

    def ask(
        self,
        session_id: str,
        question: str,
    ) -> ChatResponse:
        """
        Ask the chatbot a question.
        """

        return self.engine.chat(
            session_id=session_id,
            question=question,
        )

    def stream(
        self,
        session_id: str,
        question: str,
    ):
        """
        Stream a chatbot response.
        """

        return self.engine.stream_chat(
            session_id=session_id,
            question=question,
        )