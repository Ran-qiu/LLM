"""
Caching utilities for improving application performance.

This module provides a simple in-memory cache with TTL (time-to-live)
support for frequently accessed data.

For production use with multiple workers, consider using Redis:
- pip install redis
- Update this module to use Redis backend
"""

from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json

from app.core.logger import get_logger

logger = get_logger("cache")


class SimpleCache:
    """
    Simple in-memory cache with TTL support.

    Note: This is a single-process cache. For multi-process/distributed
    deployments, use Redis or Memcached.
    """

    def __init__(self):
        self._cache = {}
        self._expiry = {}

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        # Check if key exists and not expired
        if key in self._cache:
            if key in self._expiry:
                if datetime.utcnow() > self._expiry[key]:
                    # Expired, remove from cache
                    del self._cache[key]
                    del self._expiry[key]
                    logger.debug(f"Cache expired: {key}")
                    return None

            logger.debug(f"Cache hit: {key}")
            return self._cache[key]

        logger.debug(f"Cache miss: {key}")
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """
        Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 300 = 5 minutes)
        """
        self._cache[key] = value

        if ttl > 0:
            self._expiry[key] = datetime.utcnow() + timedelta(seconds=ttl)

        logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

    def delete(self, key: str):
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            logger.debug(f"Cache deleted: {key}")

    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        self._expiry.clear()
        logger.info("Cache cleared")

    def get_stats(self):
        """Get cache statistics."""
        return {
            "total_keys": len(self._cache),
            "expired_keys": sum(
                1 for key, expiry in self._expiry.items()
                if datetime.utcnow() > expiry
            )
        }


# Global cache instance
cache = SimpleCache()


def make_cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from arguments.

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    # Convert args and kwargs to a stable string representation
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)

    # Hash for consistent length
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results.

    Args:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        key_prefix: Prefix for cache key

    Example:
        @cached(ttl=600, key_prefix="user")
        def get_user(user_id: int):
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{make_cache_key(*args, **kwargs)}"

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)

            return result

        # Add cache management methods
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: cache.get_stats()

        return wrapper

    return decorator


# Cache invalidation helpers
class CacheInvalidator:
    """Helper class for cache invalidation patterns."""

    @staticmethod
    def invalidate_user(user_id: int):
        """Invalidate all user-related caches."""
        cache.delete(f"user:get_user:{user_id}")
        cache.delete(f"user:get_user_by_username:{user_id}")
        logger.info(f"Invalidated user cache: user_id={user_id}")

    @staticmethod
    def invalidate_conversation(conversation_id: int):
        """Invalidate all conversation-related caches."""
        cache.delete(f"conv:get_conversation:{conversation_id}")
        cache.delete(f"conv:get_messages:{conversation_id}")
        logger.info(f"Invalidated conversation cache: conversation_id={conversation_id}")

    @staticmethod
    def invalidate_api_key(api_key_id: int):
        """Invalidate API key caches."""
        cache.delete(f"apikey:get_api_key:{api_key_id}")
        logger.info(f"Invalidated API key cache: api_key_id={api_key_id}")


# ==========================================
# Usage Examples
# ==========================================

"""
1. BASIC USAGE
--------------
from app.core.caching import cache

# Set value
cache.set("my_key", {"data": "value"}, ttl=600)

# Get value
value = cache.get("my_key")

# Delete value
cache.delete("my_key")

2. DECORATOR USAGE
------------------
from app.core.caching import cached

@cached(ttl=300, key_prefix="user")
def get_user_by_id(user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# First call: fetches from database and caches
user = get_user_by_id(1)

# Second call: returns from cache
user = get_user_by_id(1)

3. CACHE INVALIDATION
--------------------
from app.core.caching import CacheInvalidator

# After updating user data
CacheInvalidator.invalidate_user(user_id)

# After updating conversation
CacheInvalidator.invalidate_conversation(conversation_id)

4. RECOMMENDED CACHING STRATEGIES
--------------------------------

# Cache user profiles (TTL: 5 minutes)
@cached(ttl=300, key_prefix="user")
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# Cache API keys (TTL: 10 minutes)
@cached(ttl=600, key_prefix="apikey")
def get_api_key(db: Session, api_key_id: int):
    return db.query(APIKey).filter(APIKey.id == api_key_id).first()

# Cache conversation metadata (TTL: 2 minutes)
@cached(ttl=120, key_prefix="conv")
def get_conversation_metadata(db: Session, conversation_id: int):
    return db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

# Don't cache: frequently changing data
# - Messages (change constantly during chat)
# - Statistics (should be real-time)
# - Search results (complex query parameters)

5. PRODUCTION REDIS INTEGRATION
-------------------------------
# For production, replace SimpleCache with Redis:

import redis
from typing import Any, Optional

class RedisCache:
    def __init__(self):
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    def delete(self, key: str):
        self.redis.delete(key)

    def clear(self):
        self.redis.flushdb()

# Then update: cache = RedisCache()
"""
