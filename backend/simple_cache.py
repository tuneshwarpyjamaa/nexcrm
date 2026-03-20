import time
from typing import Any, Dict, Optional

# Simple in-memory cache with 5-minute TTL
_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, float] = {}
TTL = 300  # 5 minutes

def get(key: str) -> Optional[Any]:
    """Get value from cache if not expired"""
    current_time = time.time()
    
    # Check if key exists and not expired
    if key in _cache and key in _cache_timestamps:
        if current_time - _cache_timestamps[key] < TTL:
            return _cache[key]['data']
        else:
            # Expired, remove it
            del _cache[key]
            del _cache_timestamps[key]
    
    return None

def set(key: str, value: Any) -> None:
    """Set value in cache with current timestamp"""
    _cache[key] = {'data': value}
    _cache_timestamps[key] = time.time()

def delete(key: str) -> None:
    """Delete entry from cache"""
    if key in _cache:
        del _cache[key]
    if key in _cache_timestamps:
        del _cache_timestamps[key]

def clear_pattern(pattern: str) -> None:
    """Clear cache entries matching pattern"""
    keys_to_delete = []
    for key in _cache:
        if pattern in key:
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        delete(key)

def clear_all() -> None:
    """Clear all cache entries"""
    _cache.clear()
    _cache_timestamps.clear()
