import time
from typing import Any


class MemoryCache:
    """Simple thread-safe in-memory cache manager with TTL support."""

    def __init__(self, default_ttl_seconds: int = 300):
        self._store: dict[str, dict[str, Any]] = {}
        self.default_ttl = default_ttl_seconds

    def get(self, key: str) -> Any | None:
        """Get cached value if not expired."""
        if key in self._store:
            item = self._store[key]
            if time.time() < item["expires_at"]:
                return item["value"]
            else:
                del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """Set cache value with TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        self._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
        }

    def delete(self, key: str) -> None:
        """Delete specific cache key."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._store.clear()


# Global cache instance
cache = MemoryCache(default_ttl_seconds=300)
