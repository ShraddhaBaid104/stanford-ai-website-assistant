"""
Production Memory Service

Provides a clean abstraction over the application's
conversation memory implementation.
"""

from __future__ import annotations

from typing import List

from app.memory.redis_memory import RedisMemory


class MemoryService:
    """
    High-level service responsible for conversation memory.
    """

    def __init__(self):

        self.memory = RedisMemory()

    def get_history(
        self,
        session_id: str,
    ) -> List[str]:
        """
        Retrieve conversation history.
        """

        return self.memory.get_history(session_id)

    def save_user_message(
        self,
        session_id: str,
        message: str,
    ) -> None:
        """
        Store a user message.
        """

        self.memory.add_user_message(
            session_id,
            message,
        )

    def save_assistant_message(
        self,
        session_id: str,
        message: str,
    ) -> None:
        """
        Store an assistant response.
        """

        self.memory.add_assistant_message(
            session_id,
            message,
        )

    def clear(
        self,
        session_id: str,
    ) -> None:
        """
        Remove conversation history.
        """

        self.memory.clear(session_id)