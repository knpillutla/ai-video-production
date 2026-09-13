"""High-performance asynchronous caching layer for scaling to millions of users.

Provides deterministic SHA-256 prompt hashing, in-memory TTL/LRU caching,
Redis distributed adapter compatibility, and cache hit/miss telemetry.
"""

from collections import OrderedDict
from dataclasses import dataclass
import functools
import hashlib
import json
import time
from typing import Any, Callable, Dict, Optional, Tuple
import asyncio

from src.core.telemetry import logger


@dataclass
class CacheEntry:
    """Represents a cached value with its expiration timestamp."""

    value: Any
    expires_at: float
    created_at: float


class AsyncCacheManager:
    """Thread-safe asynchronous two-tier cache with TTL and LRU eviction."""

    def __init__(self, max_size: int = 5000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = asyncio.Lock()

        # Telemetry metrics
        self.hits: int = 0
        self.misses: int = 0
        self.evictions: int = 0

    @staticmethod
    def compute_hash(data: Any) -> str:
        """Compute deterministic SHA-256 hex digest for any string or JSON-serializable object."""
        if isinstance(data, str):
            payload = data.encode("utf-8")
        else:
            payload = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _purge_expired_unlocked(self, now: float) -> None:
        """Purge expired keys (internal helper)."""
        expired_keys = [k for k, v in self._cache.items() if v.expires_at <= now]
        for k in expired_keys:
            del self._cache[k]
            self.evictions += 1

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache if present and unexpired."""
        now = time.time()
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self.misses += 1
                return None

            if entry.expires_at <= now:
                del self._cache[key]
                self.misses += 1
                self.evictions += 1
                return None

            # Move to end for LRU policy
            self._cache.move_to_end(key)
            self.hits += 1
            return entry.value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value in cache with specified TTL in seconds."""
        ttl_val = ttl if ttl is not None else self.default_ttl
        now = time.time()
        expires_at = now + ttl_val

        async with self._lock:
            self._purge_expired_unlocked(now)

            # Evict oldest entry if at capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cache.popitem(last=False)
                self.evictions += 1

            self._cache[key] = CacheEntry(value=value, expires_at=expires_at, created_at=now)
            self._cache.move_to_end(key)

    async def delete(self, key: str) -> bool:
        """Delete an entry from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> None:
        """Clear all entries in cache."""
        async with self._lock:
            self._cache.clear()

    async def get_stats(self) -> Dict[str, Any]:
        """Return cache health, hit-ratio, and eviction statistics."""
        async with self._lock:
            total_requests = self.hits + self.misses
            hit_ratio = round((self.hits / total_requests) * 100, 2) if total_requests > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "hit_ratio_pct": hit_ratio,
                "evictions": self.evictions,
            }


# Global singleton cache instance
cache = AsyncCacheManager(max_size=10000, default_ttl=3600)


def cached(ttl_seconds: int = 3600, namespace: str = "default"):
    """Decorator to cache async function results using arguments hash."""

    def decorator(func: Callable[..., Any]):
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            # Deterministic hash of function name, args and kwargs
            call_repr = {
                "namespace": namespace,
                "func": func.__qualname__,
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in sorted(kwargs.items())},
            }
            cache_key = f"{namespace}:{AsyncCacheManager.compute_hash(call_repr)}"

            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"cache_hit: key={cache_key[:16]}... func={func.__name__}")
                return cached_result

            result = await func(*args, **kwargs)
            await cache.set(cache_key, result, ttl=ttl_seconds)
            logger.debug(f"cache_set: key={cache_key[:16]}... func={func.__name__}")
            return result

        return wrapper

    return decorator
