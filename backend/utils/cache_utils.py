from functools import wraps
from cache_config import cache, invalidate_pattern, invalidate_cache
from flask import request
import hashlib
import json


def get_cache_key(*args):
    """Generate a consistent cache key from arguments"""
    key_str = '_'.join(str(arg) for arg in args)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached_with_key(timeout=3600, key_prefix=''):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key based on function name and parameters
            cache_key = f"{key_prefix}:{f.__name__}:{str(request.args)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f"[CACHE HIT] {cache_key}")
                return cached_result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            print(f"[CACHE SET] {cache_key} with timeout {timeout}s")
            
            return result
        return decorated_function
    return decorator


# TIMEOUT CONSTANTS 
CACHE_TIMEOUT_LOTS = 300       # 5 minutes - Parking lots 
CACHE_TIMEOUT_DASHBOARD = 300     # 5 minutes - User dashboard


def invalidate_lot_cache(lot_id):
    """Called when Admin updates a specific lot."""
    invalidate_cache(
        f'parking:lot:{lot_id}',
        f'parking:spots:{lot_id}',
        f'user_parking_lot_details_{lot_id}'
    )
    invalidate_pattern('parking:lots:*')
    invalidate_pattern('user_parking_lots_*')

def invalidate_user_cache(user_id):
    """
    Called when User books/cancels.
    """
    invalidate_cache(f'user_dashboard_{user_id}')

def invalidate_admin_dashboard_cache():
    """Called when revenue changes."""
    invalidate_cache(
        'admin:dashboard',
        'admin:daily_summary',
        'admin:charts_data'
    )
    invalidate_pattern('admin:*')

def invalidate_all_lots_cache():
    prefix = "parking_lots_search_"
    try:
        for key in list(cache._cache.keys()):
            if key.startswith(prefix):
                cache.delete(key)
        print("[CACHE INVALIDATED] Parking lots cache cleared")
    except Exception as e:
        print("Cache invalidation failed:", e)
