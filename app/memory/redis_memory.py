"""
Redis Conversation Memory

Stores conversation history using Redis.

Key format:
conversation:<session_id>

Each conversation is stored as a Redis List:

User: ...
Assistant: ...
User: ...
Assistant: ...
"""

from __future__ import annotations

from typing import List

from app.core.config import REDIS_TTL_SECONDS
from app.memory.redis_client import redis_client


class RedisMemory:
    """
    Handles conversation history stored in Redis.
    """

    def __init__(self):
        self.redis = redis_client

    def _key(self, session_id: str) -> str:
        return f"conversation:{session_id}"

    def get_history(
        self,
        session_id: str,
    ) -> List[str]:

        return self.redis.lrange(
            self._key(session_id),
            0,
            -1,
        )

    def add_user_message(
        self,
        session_id: str,
        message: str,
    ):

        key = self._key(session_id)

        self.redis.rpush(
            key,
            f"User: {message}",
        )

        self.redis.expire(
            key,
            REDIS_TTL_SECONDS,
        )

    def add_assistant_message(
        self,
        session_id: str,
        message: str,
    ):

        key = self._key(session_id)

        self.redis.rpush(
            key,
            f"Assistant: {message}",
        )

        self.redis.expire(
            key,
            REDIS_TTL_SECONDS,
        )

    def clear(
        self,
        session_id: str,
    ):

        self.redis.delete(
            self._key(session_id)
        )