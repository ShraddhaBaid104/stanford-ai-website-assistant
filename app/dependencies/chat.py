"""
Dependency injection for ChatService.

Creates ONE ChatService instance for the
entire FastAPI application.
"""

from app.services.chat_service import ChatService

chat_service = ChatService()


def get_chat_service() -> ChatService:
    """
    Return the singleton ChatService.
    """
    return chat_service