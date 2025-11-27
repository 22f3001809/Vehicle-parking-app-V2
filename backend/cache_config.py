"""Redis cache configuration and utility functions
"""

from flask_caching import Cache
import redis
import os

# Initialize Flask-Caching with Redis backend
cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
})

redis_client = redis.from_url(
    os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
)


def init_cache(app):
    """
    Initialize cache with Flask app
    
    Args:
        app: Flask application instance
    """
    cache.init_app(app)


def invalidate_cache(*keys):
    """
    Invalidate (delete) specific cache keys
    
    Args:
        *keys: Variable number of cache keys to delete
    """
    for key in keys:
        cache.delete(key)


def invalidate_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern
    
    Args:
        pattern: Pattern string (e.g., 'parking_lot_*')
    """
    try:
        # Get all keys matching pattern
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception as e:
        print(f"Error invalidating cache pattern {pattern}: {e}")


def set_cache(key, value, timeout=3600):
    """
    Set cache value with timeout
    
    Args:
        key: Cache key
        value: Value to cache
        timeout: Cache expiry time in seconds (default: 1 hour)
    """
    cache.set(key, value, timeout=timeout)


def get_cache(key):
    """
    Get value from cache
    
    Args:
        key: Cache key
        
    Returns:
        Cached value or None
    """
    return cache.get(key)
