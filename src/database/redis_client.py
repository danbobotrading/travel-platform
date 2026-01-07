"""
Redis client for Travel Platform.

This module provides Redis connection management, caching, and session storage
with async support, connection pooling, and error handling.
"""

import asyncio
import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Optional, Union, Dict, List, Set
from functools import wraps

import redis.asyncio as redis
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import (
    RedisError,
    ConnectionError,
    TimeoutError,
    AuthenticationError,
    ResponseError,
)

from src.core.config.settings import settings
from src.core.logging import logger
from src.core.exceptions import CacheError, ServiceUnavailableError


def handle_redis_errors(func):
    """Decorator to handle Redis errors consistently."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except ConnectionError as e:
            logger.error(f"Redis connection error in {func.__name__}: {e}")
            raise ServiceUnavailableError(
                message="Cache service unavailable",
                details=f"Redis connection failed: {str(e)}"
            )
        except AuthenticationError as e:
            logger.error(f"Redis authentication error in {func.__name__}: {e}")
            raise CacheError(
                message="Cache authentication failed",
                details=f"Redis authentication error: {str(e)}"
            )
        except TimeoutError as e:
            logger.error(f"Redis timeout error in {func.__name__}: {e}")
            raise CacheError(
                message="Cache operation timed out",
                details=f"Redis timeout: {str(e)}"
            )
        except ResponseError as e:
            logger.error(f"Redis response error in {func.__name__}: {e}")
            raise CacheError(
                message="Cache operation failed",
                details=f"Redis response error: {str(e)}"
            )
        except RedisError as e:
            logger.error(f"Redis error in {func.__name__}: {e}")
            raise CacheError(
                message="Cache operation failed",
                details=f"Redis error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise CacheError(
                message="Cache operation failed",
                details=f"Unexpected error: {str(e)}"
            )
    return wrapper


class RedisClient:
    """Redis client with connection pooling and async operations."""
    
    def __init__(self):
        self._redis: Optional[Redis] = None
        self._pool: Optional[ConnectionPool] = None
        self._is_connected: bool = False
        
    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        try:
            # Create connection pool
            self._pool = ConnectionPool.from_url(
                str(settings.REDIS_URL),
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            
            # Create Redis client
            self._redis = Redis(
                connection_pool=self._pool,
                decode_responses=True,  # Return strings instead of bytes
                socket_keepalive=True,
            )
            
            # Test connection
            await self._redis.ping()
            
            self._is_connected = True
            logger.info("✅ Redis connection established successfully")
            
        except ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise ServiceUnavailableError(
                message="Redis service unavailable",
                details=f"Could not connect to Redis: {str(e)}"
            )
        except AuthenticationError as e:
            logger.error(f"Redis authentication failed: {e}")
            raise CacheError(
                message="Redis authentication failed",
                details=f"Invalid Redis credentials: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during Redis initialization: {e}")
            raise CacheError(
                message="Redis initialization failed",
                details=f"Unexpected error: {str(e)}"
            )
    
    async def close(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
        
        if self._pool:
            await self._pool.disconnect()
        
        self._redis = None
        self._pool = None
        self._is_connected = False
        logger.info("Redis connection closed")
    
    @property
    def client(self) -> Redis:
        """Get Redis client instance."""
        if not self._redis:
            raise CacheError(
                message="Redis not connected",
                details="Call initialize() first"
            )
        return self._redis
    
    @handle_redis_errors
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Redis connection."""
        try:
            # Test connection
            ping_result = await self._redis.ping()
            
            # Get Redis info
            info = await self._redis.info()
            
            # Get memory usage
            memory_info = await self._redis.info('memory')
            
            # Get client list
            client_list = await self._redis.client_list()
            
            return {
                "status": "healthy" if ping_result else "unhealthy",
                "ping": ping_result,
                "version": info.get('redis_version', 'unknown'),
                "uptime_days": info.get('uptime_in_days', 0),
                "connected_clients": len(client_list),
                "used_memory_human": memory_info.get('used_memory_human', '0B'),
                "memory_fragmentation_ratio": memory_info.get('mem_fragmentation_ratio', 0),
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    # Basic key operations
    @handle_redis_errors
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        return await self._redis.get(key)
    
    @handle_redis_errors
    async def set(
        self,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = None,
        nx: bool = False,
        xx: bool = False,
    ) -> bool:
        """Set value with optional expiration."""
        # Convert non-string values to JSON
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value)
        
        if expire_seconds:
            return bool(await self._redis.set(
                key, value, ex=expire_seconds, nx=nx, xx=xx
            ))
        else:
            return bool(await self._redis.set(key, value, nx=nx, xx=xx))
    
    @handle_redis_errors
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        return await self._redis.delete(*keys)
    
    @handle_redis_errors
    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        return await self._redis.exists(*keys)
    
    @handle_redis_errors
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration time for key."""
        return bool(await self._redis.expire(key, seconds))
    
    @handle_redis_errors
    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        return await self._redis.ttl(key)
    
    # Hash operations
    @handle_redis_errors
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get field from hash."""
        return await self._redis.hget(key, field)
    
    @handle_redis_errors
    async def hgetall(self, key: str) -> Dict[str, str]:
        """Get all fields from hash."""
        return await self._redis.hgetall(key)
    
    @handle_redis_errors
    async def hset(self, key: str, field: str, value: Any) -> int:
        """Set field in hash."""
        if not isinstance(value, (str, bytes)):
            value = json.dumps(value)
        return await self._redis.hset(key, field, value)
    
    @handle_redis_errors
    async def hmset(self, key: str, mapping: Dict[str, Any]) -> bool:
        """Set multiple fields in hash."""
        # Convert values to strings
        str_mapping = {}
        for field, value in mapping.items():
            if not isinstance(value, (str, bytes)):
                str_mapping[field] = json.dumps(value)
            else:
                str_mapping[field] = value
        
        return bool(await self._redis.hmset(key, str_mapping))
    
    # List operations
    @handle_redis_errors
    async def lpush(self, key: str, *values: Any) -> int:
        """Push values to list."""
        str_values = []
        for value in values:
            if not isinstance(value, (str, bytes)):
                str_values.append(json.dumps(value))
            else:
                str_values.append(value)
        
        return await self._redis.lpush(key, *str_values)
    
    @handle_redis_errors
    async def rpush(self, key: str, *values: Any) -> int:
        """Push values to end of list."""
        str_values = []
        for value in values:
            if not isinstance(value, (str, bytes)):
                str_values.append(json.dumps(value))
            else:
                str_values.append(value)
        
        return await self._redis.rpush(key, *str_values)
    
    @handle_redis_errors
    async def lrange(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get range from list."""
        return await self._redis.lrange(key, start, end)
    
    # Set operations
    @handle_redis_errors
    async def sadd(self, key: str, *values: Any) -> int:
        """Add values to set."""
        str_values = []
        for value in values:
            if not isinstance(value, (str, bytes)):
                str_values.append(json.dumps(value))
            else:
                str_values.append(value)
        
        return await self._redis.sadd(key, *str_values)
    
    @handle_redis_errors
    async def smembers(self, key: str) -> Set[str]:
        """Get all members of set."""
        return await self._redis.smembers(key)
    
    # Sorted set operations
    @handle_redis_errors
    async def zadd(self, key: str, mapping: Dict[str, float]) -> int:
        """Add members to sorted set with scores."""
        return await self._redis.zadd(key, mapping)
    
    @handle_redis_errors
    async def zrange(self, key: str, start: int = 0, end: int = -1, withscores: bool = False) -> List:
        """Get range from sorted set."""
        return await self._redis.zrange(key, start, end, withscores=withscores)
    
    # Pattern operations
    @handle_redis_errors
    async def keys(self, pattern: str) -> List[str]:
        """Find keys matching pattern."""
        return await self._redis.keys(pattern)
    
    @handle_redis_errors
    async def scan_iter(self, pattern: str = "*", count: int = 100) -> List[str]:
        """Iterate over keys matching pattern (memory efficient)."""
        keys = []
        async for key in self._redis.scan_iter(match=pattern, count=count):
            keys.append(key)
        return keys
    
    # Atomic operations
    @handle_redis_errors
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment integer value atomically."""
        return await self._redis.incrby(key, amount)
    
    @handle_redis_errors
    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement integer value atomically."""
        return await self._redis.decrby(key, amount)
    
    # Cache-specific operations
    @handle_redis_errors
    async def cache_get(
        self,
        key: str,
        default: Any = None,
        deserialize: bool = True,
    ) -> Any:
        """Get value from cache with optional deserialization."""
        value = await self.get(key)
        
        if value is None:
            return default
        
        if deserialize:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Try to unpickle if not JSON
                try:
                    return pickle.loads(value.encode() if isinstance(value, str) else value)
                except:
                    return value
        
        return value
    
    @handle_redis_errors
    async def cache_set(
        self,
        key: str,
        value: Any,
        expire_seconds: Optional[int] = None,
        serialize: bool = True,
    ) -> bool:
        """Set value in cache with optional serialization."""
        if serialize and not isinstance(value, (str, bytes)):
            try:
                value = json.dumps(value)
            except (TypeError, OverflowError):
                # Fallback to pickle for complex objects
                value = pickle.dumps(value)
        
        if expire_seconds is None:
            expire_seconds = settings.REDIS_CACHE_TTL
        
        return await self.set(key, value, expire_seconds)
    
    @handle_redis_errors
    async def cache_delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        keys = await self.keys(pattern)
        if keys:
            return await self.delete(*keys)
        return 0
    
    # Session operations
    @handle_redis_errors
    async def session_get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        key = f"session:{session_id}"
        data = await self.get(key)
        
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                logger.warning(f"Invalid session data for {session_id}")
                await self.delete(key)
        
        return None
    
    @handle_redis_errors
    async def session_set(
        self,
        session_id: str,
        data: Dict[str, Any],
        expire_seconds: Optional[int] = None,
    ) -> bool:
        """Set session data."""
        key = f"session:{session_id}"
        
        if expire_seconds is None:
            expire_seconds = settings.REDIS_SESSION_TTL
        
        return await self.set(key, json.dumps(data), expire_seconds)
    
    @handle_redis_errors
    async def session_delete(self, session_id: str) -> int:
        """Delete session."""
        key = f"session:{session_id}"
        return await self.delete(key)
    
    # Rate limiting
    @handle_redis_errors
    async def rate_limit(
        self,
        key: str,
        limit: int,
        period: int,
    ) -> Dict[str, Any]:
        """Implement rate limiting."""
        current = await self.incr(key)
        
        if current == 1:
            await self.expire(key, period)
        
        remaining = max(0, limit - current)
        reset_time = await self.ttl(key)
        
        return {
            "limit": limit,
            "remaining": remaining,
            "reset": reset_time,
            "current": current,
            "is_exceeded": current > limit,
        }
    
    # Pub/Sub
    @handle_redis_errors
    async def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel."""
        if not isinstance(message, (str, bytes)):
            message = json.dumps(message)
        
        return await self._redis.publish(channel, message)
    
    @handle_redis_errors
    async def subscribe(self, channel: str):
        """Subscribe to channel."""
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
    
    # Transaction support
    @handle_redis_errors
    async def pipeline(self):
        """Create pipeline for transaction."""
        return self._redis.pipeline()
    
    # Utility methods
    async def flush_all(self) -> bool:
        """Flush all Redis data (use with caution!)."""
        if settings.APP_ENV == "production":
            logger.warning("Attempt to flush Redis in production!")
            return False
        
        result = await self._redis.flushall()
        logger.info("Redis flushed successfully")
        return bool(result)
    
    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        info = await self._redis.info()
        return {
            "version": info.get("redis_version"),
            "mode": info.get("redis_mode"),
            "os": info.get("os"),
            "uptime_days": info.get("uptime_in_days"),
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "total_commands_processed": info.get("total_commands_processed"),
            "instantaneous_ops_per_sec": info.get("instantaneous_ops_per_sec"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "hit_rate": (
                info.get("keyspace_hits", 0)
                / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
            ),
        }


# Global Redis client instance
redis_client = RedisClient()


# FastAPI dependency
async def get_redis() -> RedisClient:
    """Get Redis client for dependency injection."""
    return redis_client
