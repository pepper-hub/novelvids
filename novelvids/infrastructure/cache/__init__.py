"""Cache infrastructure using Redis."""

import json
from typing import Any

import redis.asyncio as redis
from loguru import logger

from novelvids.core.config import settings


class RedisCache:
    """Redis cache implementation."""

    def __init__(self, url: str | None = None) -> None:
        self.url = url or settings.redis.get_connection_url()
        self._client: redis.Redis | None = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self._client = redis.from_url(self.url, decode_responses=True)
        try:
            await self._client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self._client = None

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._client = None

    @property
    def client(self) -> redis.Redis:
        """Get Redis client."""
        if self._client is None:
            raise RuntimeError("Redis not connected")
        return self._client

    async def get(self, key: str) -> Any | None:
        """Get value from cache."""
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """Set value in cache with optional TTL."""
        try:
            serialized = json.dumps(value)
            if ttl:
                await self.client.setex(key, ttl, serialized)
            else:
                await self.client.set(key, serialized)
            return True
        except Exception as e:
            logger.warning(f"Cache set error for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            await self.client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete error for {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.warning(f"Cache exists error for {key}: {e}")
            return False

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment value in cache."""
        return await self.client.incrby(key, amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement value in cache."""
        return await self.client.decrby(key, amount)

    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to list."""
        serialized = [json.dumps(v) for v in values]
        return await self.client.lpush(key, *serialized)

    async def rpop(self, key: str) -> Any | None:
        """Pop value from list."""
        value = await self.client.rpop(key)
        if value:
            return json.loads(value)
        return None

    async def lrange(self, key: str, start: int, end: int) -> list[Any]:
        """Get range from list."""
        values = await self.client.lrange(key, start, end)
        return [json.loads(v) for v in values]
