import redis.asyncio as redis
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Singleton Redis connection manager"""
    
    _instance = None
    _redis_client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self):
        """Establish connection to Redis"""
        if self._redis_client is None:
            try:
                self._redis_client = await redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("Connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
    
    async def disconnect(self):
        """Close Redis connection"""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> str | None:
        """Get value from cache"""
        if not self._redis_client:
            await self.connect()
        try:
            return await self._redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = None):
        """Set value in cache with optional TTL"""
        if not self._redis_client:
            await self.connect()
        try:
            if ttl:
                await self._redis_client.setex(key, ttl, value)
            else:
                await self._redis_client.set(key, value)
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache"""
        if not self._redis_client:
            await self.connect()
        try:
            await self._redis_client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")


# Global cache instance
cache = RedisCache()
