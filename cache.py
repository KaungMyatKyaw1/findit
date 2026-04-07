"""
cache.py — Thread-safe in-memory cache with automatic expiry.

Two public functions:
  get(key)           — returns cached products, or None if missing/expired
  set(key, products) — saves products under key with a fresh timestamp
"""

import time
import threading


EXPIRY_SECONDS = 3600  # Cached results stay valid for 1 hour

# Internal storage — kept private so callers always go through get/set
_store: dict = {}
_lock = threading.Lock()


def get(key: str) -> list | None:
    """Return the cached product list for key, or None if missing or expired."""
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return None
        if time.time() - entry["timestamp"] > EXPIRY_SECONDS:
            del _store[key]  # Clean up stale entry
            return None
        return list(entry["products"])  # Return a shallow copy


def set(key: str, products: list) -> None:
    """Store products under key and record the current time."""
    with _lock:
        _store[key] = {
            "products":  products,
            "timestamp": time.time(),
        }
