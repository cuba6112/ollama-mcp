"""Simple in-memory cache for Ollama MCP Server"""
import time
from typing import Dict, Any, Optional, Tuple
from functools import wraps
import asyncio
import logging

from .config import settings

logger = logging.getLogger(__name__)


class SimpleCache:
    """Simple TTL-based in-memory cache"""
    
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = asyncio.Lock()
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        async with self._lock:
            if key not in self._cache:
                return None
                
            value, expiry = self._cache[key]
            if time.time() > expiry:
                del self._cache[key]
                return None
                
            return value
            
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = settings.cache_ttl
            
        async with self._lock:
            expiry = time.time() + ttl
            self._cache[key] = (value, expiry)
            
    async def delete(self, key: str) -> None:
        """Delete key from cache"""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                
    async def clear(self) -> None:
        """Clear all cache entries"""
        async with self._lock:
            self._cache.clear()
            
    async def cleanup_expired(self) -> None:
        """Remove expired entries"""
        async with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if current_time > expiry
            ]
            for key in expired_keys:
                del self._cache[key]
                
            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")


# Global cache instance
cache = SimpleCache()


def cached(key_prefix: str, ttl: Optional[int] = None):
    """Decorator for caching async function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not settings.enable_cache:
                return await func(*args, **kwargs)
                
            # Create cache key from function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}"
            if args or kwargs:
                # Simple key generation - can be improved
                cache_key += f":{hash((args, tuple(sorted(kwargs.items()))))}"
                
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
                
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator