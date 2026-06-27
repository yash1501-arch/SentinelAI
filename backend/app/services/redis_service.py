"""
Redis caching service for SentinelAI.

Handles conversation context caching, session management,
and forecast result caching.
"""
import json
from typing import Optional, List, Dict, Any
from datetime import timedelta
from loguru import logger

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings


class RedisService:
    """Async Redis service for caching and session management."""

    _client: Optional[Any] = None

    @classmethod
    async def get_client(cls):
        """Get or create Redis client."""
        if not REDIS_AVAILABLE:
            logger.warning("redis package not installed, caching disabled")
            return None

        if cls._client is None:
            try:
                cls._client = aioredis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                )
                # Test connection
                await cls._client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                cls._client = None
        return cls._client

    @classmethod
    async def close(cls):
        """Close Redis connection."""
        if cls._client:
            await cls._client.close()
            cls._client = None

    # --- Conversation Context Caching ---

    @classmethod
    async def cache_conversation_context(
        cls, session_id: str, messages: List[Dict], ttl: int = 3600
    ) -> bool:
        """Cache conversation messages for a session."""
        client = await cls.get_client()
        if not client:
            return False
        try:
            key = f"conv:{session_id}"
            await client.set(key, json.dumps(messages), ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
            return False

    @classmethod
    async def get_conversation_context(cls, session_id: str) -> Optional[List[Dict]]:
        """Retrieve cached conversation context."""
        client = await cls.get_client()
        if not client:
            return None
        try:
            key = f"conv:{session_id}"
            data = await client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
            return None

    # --- Forecast Caching ---

    @classmethod
    async def cache_forecast(
        cls, forecast_type: str, data: Dict, ttl: int = 21600
    ) -> bool:
        """Cache forecast results (6-hour default TTL)."""
        client = await cls.get_client()
        if not client:
            return False
        try:
            key = f"forecast:{forecast_type}"
            await client.set(key, json.dumps(data, default=str), ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis forecast cache error: {e}")
            return False

    @classmethod
    async def get_cached_forecast(cls, forecast_type: str) -> Optional[Dict]:
        """Retrieve cached forecast."""
        client = await cls.get_client()
        if not client:
            return None
        try:
            key = f"forecast:{forecast_type}"
            data = await client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis forecast get error: {e}")
            return None

    # --- Session Management ---

    @classmethod
    async def set_user_session(cls, user_id: str, session_data: Dict, ttl: int = 1800) -> bool:
        """Store user session data (30-min default TTL)."""
        client = await cls.get_client()
        if not client:
            return False
        try:
            key = f"session:{user_id}"
            await client.set(key, json.dumps(session_data, default=str), ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis session set error: {e}")
            return False

    @classmethod
    async def get_user_session(cls, user_id: str) -> Optional[Dict]:
        """Retrieve user session data."""
        client = await cls.get_client()
        if not client:
            return None
        try:
            key = f"session:{user_id}"
            data = await client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis session get error: {e}")
            return None

    # --- Alert Caching ---

    @classmethod
    async def cache_alerts(cls, alerts: List[Dict], ttl: int = 900) -> bool:
        """Cache generated alerts (15-min default TTL)."""
        client = await cls.get_client()
        if not client:
            return False
        try:
            await client.set("alerts:current", json.dumps(alerts, default=str), ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis alert cache error: {e}")
            return False

    @classmethod
    async def get_cached_alerts(cls) -> Optional[List[Dict]]:
        """Retrieve cached alerts."""
        client = await cls.get_client()
        if not client:
            return None
        try:
            data = await client.get("alerts:current")
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis alert get error: {e}")
            return None

    # --- Generic Cache ---

    @classmethod
    async def set(cls, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a generic cache value."""
        client = await cls.get_client()
        if not client:
            return False
        try:
            serialized = json.dumps(value, default=str) if not isinstance(value, str) else value
            await client.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    @classmethod
    async def get(cls, key: str) -> Optional[str]:
        """Get a generic cache value."""
        client = await cls.get_client()
        if not client:
            return None
        try:
            return await client.get(key)
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    @classmethod
    async def delete(cls, key: str) -> bool:
        """Delete a cache key."""
        client = await cls.get_client()
        if not client:
            return False
        try:
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
