"""Caching utilities."""

import json
from typing import Any, Optional

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class CacheClient:
    """Async Redis cache client."""

    def __init__(self, redis_url: str):
        """
        Initialize cache client.

        Args:
            redis_url: Redis connection URL
        """
        if aioredis is None:
            raise ImportError("redis package is required for caching")

        self.redis_url = redis_url
        self._client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self._client = await aioredis.from_url(self.redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None
        """
        if not self._client:
            return None

        value = await self._client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        if not self._client:
            return False

        try:
            serialized = json.dumps(value)
        except (TypeError, ValueError):
            serialized = str(value)

        if ttl:
            return await self._client.setex(key, ttl, serialized)
        else:
            return await self._client.set(key, serialized)

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False otherwise
        """
        if not self._client:
            return False

        result = await self._client.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        if not self._client:
            return False

        return await self._client.exists(key) > 0
