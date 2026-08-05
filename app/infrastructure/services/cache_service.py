import json
import logging
from typing import Any, Optional

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None

logger = logging.getLogger(__name__)


class RedisCacheService:
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self._client: Optional[Any] = None

    async def connect(self) -> None:
        if not self.redis_url or aioredis is None:
            logger.info("Redis cache disabled or redis dependency missing.")
            return

        try:
            self._client = aioredis.from_url(
                self.redis_url,
                decode_responses=True,
            )
            # Test connection
            await self._client.ping()
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as exc:
            logger.warning(f"Could not connect to Redis at {self.redis_url}: {exc}")
            self._client = None

    async def close(self) -> None:
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as exc:
                logger.warning(f"Error closing Redis connection: {exc}")
            finally:
                self._client = None

    @property
    def is_connected(self) -> bool:
        return self._client is not None

    async def get_json(self, key: str) -> Optional[Any]:
        if not self.is_connected:
            return None
        try:
            raw_data = await self._client.get(key)
            if raw_data:
                return json.loads(raw_data)
        except Exception as exc:
            logger.warning(f"Redis get_json failed for key '{key}': {exc}")
        return None

    async def set_json(self, key: str, value: Any, ttl: int = 300) -> bool:
        if not self.is_connected:
            return False
        try:
            serialized = json.dumps(value)
            await self._client.set(key, serialized, ex=ttl)
            return True
        except Exception as exc:
            logger.warning(f"Redis set_json failed for key '{key}': {exc}")
            return False

    async def delete(self, key: str) -> bool:
        if not self.is_connected:
            return False
        try:
            await self._client.delete(key)
            return True
        except Exception as exc:
            logger.warning(f"Redis delete failed for key '{key}': {exc}")
            return False

    async def pop_json(self, key: str) -> Optional[Any]:
        if not self.is_connected:
            return None
        try:
            raw_data = await self._client.execute_command("GETDEL", key)
            if raw_data:
                return json.loads(raw_data)
        except Exception as exc:
            logger.warning(f"Redis pop_json failed for key '{key}': {exc}")
        return None

    async def delete_pattern(self, pattern: str) -> bool:
        if not self.is_connected:
            return False
        try:
            keys = await self._client.keys(pattern)
            if keys:
                await self._client.delete(*keys)
            return True
        except Exception as exc:
            logger.warning(f"Redis delete_pattern failed for pattern '{pattern}': {exc}")
            return False
