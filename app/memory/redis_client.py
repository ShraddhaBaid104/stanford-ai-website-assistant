"""
Redis Client

Creates a singleton Redis connection used throughout the application.
"""

from redis import Redis

from app.core.config import (
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DB,
)

redis_client = Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
)

try:
    redis_client.ping()
except Exception as exc:
    raise RuntimeError(
        f"Unable to connect to Redis: {exc}"
    ) from exc