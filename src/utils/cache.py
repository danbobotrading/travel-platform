"""
Redis-based caching utilities for Travel Platform.
Includes decorators for async function caching.
"""
import asyncio
import json
import pickle
from typing import Any, Callable, Optional, TypeVar, Union
from datetime import timedelta
from functools import wraps
import hashlib

from ..core.config.settings import settings
from .logger import logger

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis_not_available", message="Redis caching disabled")


T = TypeVar('T')
R = TypeVar('R')


class RedisCache:
    """Redis caching client with async support."""
    
    def __init__(self, redis_url: Optional[str] = None, prefix: Optional[str] = None):
        self._client: Optional[redis.Redis] = None
        self.redis_url = redis_url or str(settings.REDIS_URL)
        self.prefix = prefix or getattr(settings, 'CACHE_PREFIX', 'travel')
        self._connected = False
    
    async def _ensure_connection(self) -> bool:
        """Ensure Redis connection is established."""
        if not REDIS_AVAILABLE:
            return False
        
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=False,  # We'll handle encoding/decoding
                    socket_connect_timeout=5.0,
                    socket_keepalive=True
                )
                await self._client.ping()
                self._connected = True
                logger.debug("redis_connected", url=self.redis_url)
            except Exception as e:
                logger.error("redis_connection_failed", error=str(e))
                self._connected = False
                self._client = None
        
        return self._connected
    
    def _make_key(self, key: str) -> str:
        """Create a namespaced cache key."""
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        if not await self._ensure_connection():
            return default
        
        try:
            cache_key = self._make_key(key)
            data = await self._client.get(cache_key)
            
            if data is None:
                return default
            
            # Try to deserialize
            try:
                return pickle.loads(data)
            except:
                # Fallback to JSON
                return json.loads(data.decode('utf-8'))
                
        except Exception as e:
            logger.warning("cache_get_failed", key=key, error=str(e))
            return default
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL."""
        if not await self._ensure_connection():
            return False
        
        try:
            cache_key = self._make_key(key)
            
            # Try to pickle first (supports more types)
            try:
                data = pickle.dumps(value)
            except:
                # Fallback to JSON
                data = json.dumps(value).encode('utf-8')
            
            if ttl is None:
                ttl = getattr(settings, 'CACHE_TTL', 300)
            
            await self._client.setex(cache_key, ttl, data)
            logger.debug("cache_set", key=key, ttl=ttl)
            return True
            
        except Exception as e:
            logger.warning("cache_set_failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if not await self._ensure_connection():
            return False
        
        try:
            cache_key = self._make_key(key)
            result = await self._client.delete(cache_key)
            return result > 0
        except Exception as e:
            logger.warning("cache_delete_failed", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if not await self._ensure_connection():
            return False
        
        try:
            cache_key = self._make_key(key)
            return await self._client.exists(cache_key) > 0
        except Exception as e:
            logger.warning("cache_exists_failed", key=key, error=str(e))
            return False
    
    async def clear_prefix(self, prefix: str) -> int:
        """Clear all keys with given prefix."""
        if not await self._ensure_connection():
            return 0
        
        try:
            pattern = self._make_key(f"{prefix}:*")
            keys = await self._client.keys(pattern)
            
            if keys:
                await self._client.delete(*keys)
            
            logger.debug("cache_cleared_prefix", prefix=prefix, keys_deleted=len(keys))
            return len(keys)
        except Exception as e:
            logger.warning("cache_clear_prefix_failed", prefix=prefix, error=str(e))
            return 0
    
    async def ttl(self, key: str) -> Optional[int]:
        """Get TTL for a key."""
        if not await self._ensure_connection():
            return None
        
        try:
            cache_key = self._make_key(key)
            ttl = await self._client.ttl(cache_key)
            return ttl if ttl > 0 else None
        except Exception as e:
            logger.warning("cache_ttl_failed", key=key, error=str(e))
            return None
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter in cache."""
        if not await self._ensure_connection():
            return None
        
        try:
            cache_key = self._make_key(key)
            return await self._client.incrby(cache_key, amount)
        except Exception as e:
            logger.warning("cache_increment_failed", key=key, error=str(e))
            return None
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._connected = False


# Global cache instance
_cache_instance: Optional[RedisCache] = None


async def get_cache() -> RedisCache:
    """Get or create Redis cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
    return _cache_instance


def cache_key_builder(*args, **kwargs) -> str:
    """Build cache key from function arguments."""
    # Create a string representation of args and kwargs
    key_parts = []
    
    for arg in args:
        if isinstance(arg, (str, int, float, bool, type(None))):
            key_parts.append(str(arg))
        else:
            key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    return "_".join(key_parts)


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    unless: Optional[Callable[..., bool]] = None
):
    """
    Decorator for caching async function results in Redis.
    
    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache key
        unless: Callable that returns True to skip caching
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Check if we should skip caching
            if unless and unless(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Build cache key
            func_name = func.__name__
            arg_key = cache_key_builder(*args, **kwargs)
            cache_key = f"{key_prefix}:{func_name}:{arg_key}" if key_prefix else f"{func_name}:{arg_key}"
            
            # Try to get from cache
            cache = await get_cache()
            cached_value = await cache.get(cache_key)
            
            if cached_value is not None:
                logger.debug("cache_hit", function=func_name, key=cache_key)
                return cached_value
            
            # Not in cache, execute function
            logger.debug("cache_miss", function=func_name, key=cache_key)
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(key_pattern: str):
    """
    Decorator to invalidate cache after function execution.
    
    Args:
        key_pattern: Pattern to match cache keys (supports * wildcard)
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Execute function
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            cache = await get_cache()
            keys_deleted = await cache.clear_prefix(key_pattern)
            
            if keys_deleted > 0:
                logger.debug("cache_invalidated", 
                           function=func.__name__, 
                           pattern=key_pattern,
                           keys_deleted=keys_deleted)
            
            return result
        
        return wrapper
    return decorator


class CacheManager:
    """Manager for cache operations."""
    
    @staticmethod
    async def cache_user_data(user_id: str, data_key: str, data: Any, ttl: int = 3600) -> bool:
        """Cache user-specific data."""
        cache = await get_cache()
        key = f"user:{user_id}:{data_key}"
        return await cache.set(key, data, ttl)
    
    @staticmethod
    async def get_user_data(user_id: str, data_key: str, default: Any = None) -> Any:
        """Get cached user data."""
        cache = await get_cache()
        key = f"user:{user_id}:{data_key}"
        return await cache.get(key, default)
    
    @staticmethod
    async def invalidate_user_cache(user_id: str) -> int:
        """Invalidate all cache for a user."""
        cache = await get_cache()
        return await cache.clear_prefix(f"user:{user_id}")
    
    @staticmethod
    async def cache_currency_rates(rates: dict, ttl: int = 3600) -> bool:
        """Cache currency exchange rates."""
        cache = await get_cache()
        return await cache.set("currency:rates", rates, ttl)
    
    @staticmethod
    async def get_cached_currency_rates(default: dict = None) -> dict:
        """Get cached currency rates."""
        cache = await get_cache()
        return await cache.get("currency:rates", default or {})
    
    @staticmethod
    async def cache_search_results(
        search_type: str, 
        params: dict, 
        results: list, 
        ttl: int = 600
    ) -> bool:
        """Cache search results."""
        cache = await get_cache()
        param_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:16]
        key = f"search:{search_type}:{param_hash}"
        return await cache.set(key, results, ttl)
    
    @staticmethod
    async def get_cached_search_results(
        search_type: str, 
        params: dict, 
        default: list = None
    ) -> list:
        """Get cached search results."""
        cache = await get_cache()
        param_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()[:16]
        key = f"search:{search_type}:{param_hash}"
        return await cache.get(key, default or [])


async def cleanup_cache():
    """Cleanup cache resources."""
    global _cache_instance
    if _cache_instance:
        await _cache_instance.close()
        _cache_instance = None


# Test function
async def test_cache():
    """Test cache functionality."""
    if not REDIS_AVAILABLE:
        print("⚠️ Redis not available, using mock cache")
        return
    
    cache = await get_cache()
    
    print("Testing Redis Cache...")
    print("=" * 40)
    
    # Test basic set/get
    test_key = "test:basic"
    test_value = {"message": "Hello Redis", "timestamp": "2024-01-08"}
    
    await cache.set(test_key, test_value, ttl=10)
    retrieved = await cache.get(test_key)
    
    print(f"1. Basic set/get: {retrieved == test_value}")
    
    # Test exists
    exists = await cache.exists(test_key)
    print(f"2. Key exists: {exists}")
    
    # Test TTL
    ttl = await cache.ttl(test_key)
    print(f"3. TTL: {ttl} seconds")
    
    # Test increment
    counter_key = "test:counter"
    await cache.delete(counter_key)
    result1 = await cache.increment(counter_key)
    result2 = await cache.increment(counter_key, 5)
    print(f"4. Increment: {result1}, then {result2}")
    
    # Test decorator
    @cached(ttl=5)
    async def expensive_operation(x: int) -> int:
        print(f"   Computing {x} * 2...")
        return x * 2
    
    print("5. Cache decorator test:")
    result_a = await expensive_operation(10)
    print(f"   First call: {result_a} (should compute)")
    result_b = await expensive_operation(10)
    print(f"   Second call: {result_b} (should be cached)")
    
    # Cleanup
    await cache.delete(test_key)
    await cache.delete(counter_key)
    
    print("\n✅ Cache test complete!")


if __name__ == "__main__":
    asyncio.run(test_cache())
