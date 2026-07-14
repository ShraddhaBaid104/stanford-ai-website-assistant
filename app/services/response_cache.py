"""
Redis Response Cache
"""

import hashlib
import json

import redis

from app.core.config import REDIS_HOST, REDIS_PORT


class ResponseCache:

    def __init__(self):

        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
        )

    def _key(
        self,
        session_id: str,
        question: str,
    ) -> str:

        digest = hashlib.sha256(
            question.strip().lower().encode()
        ).hexdigest()

        return f"response:{session_id}:{digest}"

    def get(
        self,
        session_id: str,
        question: str,
    ):

        data = self.redis.get(
            self._key(session_id, question)
        )

        if not data:
            return None

        return json.loads(data)

    def save(
        self,
        session_id: str,
        question: str,
        response: dict,
        ttl: int = 3600,
    ):

        self.redis.setex(
            self._key(session_id, question),
            ttl,
            json.dumps(response),
        )


# Singleton instance
response_cache = ResponseCache()