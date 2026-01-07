"""
Redis-based caching decorators for Travel Platform.
"""

import asyncio
import json
import hashlib
from typing import Any, Callable, Optional, List
from functools import wraps

from src.core.config.settings import settings
from src.database.redis_client import get_redis
from src.travel_platform.utils.logger import get_logger

logger = get_logger(__name__)


def generate_cache_key(func_name: str, args: tuple, kwargs: dict, exclude_args: List[str] = None) -> str:
    """Generate a cache key from function signature."""
    exclude_args = exclude_args or []
    
    key_parts = ["travel_platform", func_name]
    
    # Add args
    for i, arg in enumerate(args):
        key_parts.append(f"arg_{i}:{hashlib.md5(str(arg).encode()).hexdigest()}")
    
    # Add kwargs
    for key, value in kwargs.items():
        if key not in exclude_args:
            key_parts.append(f"{key}:{hashlib.md5(str(value).encode()).hexdigest()}")
    
    key_string = ":".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    
    return f"travel_platform:{func_name}:{key_hash}"


def async_cache(ttl: int = 300, exclude_args: List[str] = None):
    """Decorator for caching async function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(func.__name__, args, kwargs, exclude_args)
            
            # Try to get from cache
            try:
                redis_client = await get_redis()
                cached = await redis_client.get(cache_key)
                if cached is not None:
                    logger.debug("cache_hit", key=cache_key, function=func.__name__)
                    return json.loads(cached)
            except Exception as e:
                logger.warning("cache_get_error", error=str(e), key=cache_key)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            try:
                redis_client = await get_redis()
                await redis_client.set(cache_key, json.dumps(result), ex=ttl)
                logger.debug("cache_set", key=cache_key, ttl=ttl, function=func.__name__)
            except Exception as e:
                logger.warning("cache_set_error", error=str(e), key=cache_key)
            
            return result
        
        return wrapper
    return decorator


def cache(ttl: int = 300, exclude_args: List[str] = None):
    """Decorator for caching sync function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = generate_cache_key(func.__name__, args, kwargs, exclude_args)
            
            # Try to get from cache (sync wrapper)
            try:
                redis_client = asyncio.run(get_redis())
                cached = asyncio.run(redis_client.get(cache_key))
                if cached is not None:
                    logger.debug("cache_hit", key=cache_key, function=func.__name__)
                    return json.loads(cached)
            except Exception as e:
                logger.warning("cache_get_error", error=str(e), key=cache_key)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            try:
                redis_client = asyncio.run(get_redis())
                asyncio.run(redis_client.set(cache_key, json.dumps(result), ex=ttl))
                logger.debug("cache_set", key=cache_key, ttl=ttl, function=func.__name__)
            except Exception as e:
                logger.warning("cache_set_error", error=str(e), key=cache_key)
            
            return result
        
        return wrapper
    return decorator
