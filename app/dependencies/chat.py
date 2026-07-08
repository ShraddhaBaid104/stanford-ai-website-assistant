"""
Dependency providers for the Stanford AI Website Assistant.

This module centralizes FastAPI dependency injection.

Author: Shraddha Nahata
"""

from app.services.chat_service import ChatService


def get_chat_service() -> ChatService:
    """
    Returns the application's chat service.

    FastAPI will inject this dependency wherever required.
    """

    return ChatService()