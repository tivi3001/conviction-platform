"""TTL-based caching system for fundamental data."""

import time
import threading
from typing import Any, Optional, Dict


class TTLCache:
    """Thread-safe cache with time-to-live expiration."""

    def __init__(self):
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._detail_cache: Dict[str, tuple[Any, float]] = {}  # Lazy-loaded details
        self._pending_details: Dict[str, bool] = {}  # Track in-flight detail loads
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        with self._lock:
            if key not in self._cache:
                return None

            value, expiry_time = self._cache[key]
            if time.time() > expiry_time:
                del self._cache[key]
                return None

            return value

    def set(self, key: str, value: Any, ttl: int) -> None:
        """Set value in cache with TTL in seconds."""
        with self._lock:
            expiry_time = time.time() + ttl
            self._cache[key] = (value, expiry_time)

    def clear(self, key: str) -> None:
        """Manually clear a cache key."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]

    def clear_all(self) -> None:
        """Clear entire cache."""
        with self._lock:
            self._cache.clear()

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return self.get(key) is not None

    def get_ttl_remaining(self, key: str) -> Optional[float]:
        """Get remaining TTL for a key in seconds."""
        with self._lock:
            if key not in self._cache:
                return None

            value, expiry_time = self._cache[key]
            remaining = expiry_time - time.time()
            if remaining <= 0:
                del self._cache[key]
                return None

            return remaining

    # === NEW: Detail-level caching for lazy-loaded analysis ===

    def get_detail(self, symbol: str) -> Optional[Any]:
        """Get cached detailed analysis for a stock if available and not expired.

        Used for lazy-loaded detail modals (news, catalysts, thesis).
        """
        detail_key = f"detail_{symbol}"

        with self._lock:
            if detail_key not in self._detail_cache:
                return None

            value, expiry_time = self._detail_cache[detail_key]
            if time.time() > expiry_time:
                del self._detail_cache[detail_key]
                return None

            return value

    def set_detail(self, symbol: str, detail_data: Any, ttl: int = 3600) -> None:
        """Cache detailed analysis for a stock (separate from basic scores).

        Args:
            symbol: Stock ticker symbol
            detail_data: Detailed analysis object (complete news, catalysts, thesis)
            ttl: Time-to-live in seconds (default 1 hour)
        """
        detail_key = f"detail_{symbol}"

        with self._lock:
            expiry_time = time.time() + ttl
            self._detail_cache[detail_key] = (detail_data, expiry_time)

            # Clear pending flag
            if detail_key in self._pending_details:
                del self._pending_details[detail_key]

    def mark_pending_detail(self, symbol: str) -> None:
        """Mark that a detail load is in progress to avoid duplicate fetches.

        Args:
            symbol: Stock ticker symbol
        """
        detail_key = f"detail_{symbol}"

        with self._lock:
            self._pending_details[detail_key] = True

    def is_detail_pending(self, symbol: str) -> bool:
        """Check if a detail load is already in progress.

        Args:
            symbol: Stock ticker symbol

        Returns:
            True if detail fetch is in flight, False otherwise
        """
        detail_key = f"detail_{symbol}"

        with self._lock:
            return self._pending_details.get(detail_key, False)

    def clear_detail(self, symbol: str) -> None:
        """Manually clear cached details for a stock.

        Args:
            symbol: Stock ticker symbol
        """
        detail_key = f"detail_{symbol}"

        with self._lock:
            if detail_key in self._detail_cache:
                del self._detail_cache[detail_key]
            if detail_key in self._pending_details:
                del self._pending_details[detail_key]

    def clear_all_details(self) -> None:
        """Clear all cached detail analysis."""
        with self._lock:
            self._detail_cache.clear()
            self._pending_details.clear()

    def get_detail_cache_stats(self) -> dict:
        """Get statistics about detail cache usage.

        Returns:
            Dictionary with cache stats (size, entries, memory usage estimate)
        """
        with self._lock:
            return {
                "detail_entries": len(self._detail_cache),
                "pending_details": len(self._pending_details),
                "basic_cache_entries": len(self._cache),
            }
