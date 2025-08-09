import time
import asyncio
from typing import Optional
from app.config import settings

# Attempt to use aioredis if REDIS_URL is provided; otherwise use in-memory cache
_redis = None
_redis_client_initialized = False
try:
    import aioredis
    _aioredis_available = True
except Exception:
    _aioredis_available = False

# Simple in-memory TTL cache fallback
_in_memory_cache = {}
_in_memory_lock = asyncio.Lock()

async def get_redis():
    global _redis, _redis_client_initialized
    if not settings.REDIS_URL or not _aioredis_available:
        return None
    if _redis_client_initialized and _redis is not None:
        return _redis
    _redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    _redis_client_initialized = True
    return _redis

async def cache_get(key: str):
    """
    Try Redis first (if configured). Otherwise use in-memory fallback.
    """
    redis = await get_redis()
    if redis:
        return await redis.get(key)
    # in-memory
    async with _in_memory_lock:
        entry = _in_memory_cache.get(key)
        if not entry:
            return None
        value, expires_at = entry
        if expires_at is None or expires_at > time.time():
            return value
        # expired
        _in_memory_cache.pop(key, None)
        return None

async def cache_set(key: str, value: str, ex: Optional[int] = None):
    redis = await get_redis()
    if redis:
        if ex:
            await redis.set(key, value, ex=ex)
        else:
            await redis.set(key, value)
        return
    async with _in_memory_lock:
        expires_at = time.time() + ex if ex else None
        _in_memory_cache[key] = (value, expires_at)
