"""
Cache Strategy:
1. Parking Lots - Cached for 1 hour (updated when admin modifies)
2. Available Spots - Cached for 5 minutes (frequently changes)
3. Dashboard Stats - Cached for 5 minutes (user-specific)
4. Admin Dashboard - Cached for 10 minutes (aggregated data)
"""

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
CACHE_TIMEOUT_LOTS = 3600        # 1 hour - Parking lots (admin rarely changes)
CACHE_TIMEOUT_SPOTS = 300         # 5 minutes - Available spots (frequently changes)
CACHE_TIMEOUT_DASHBOARD = 300     # 5 minutes - User dashboard
CACHE_TIMEOUT_ADMIN_DASH = 600    # 10 minutes - Admin dashboard
CACHE_TIMEOUT_STATS = 900         # 15 minutes - Statistics


CACHE_KEY_PARKING_LOTS = 'parking:lots:*'
CACHE_KEY_PARKING_LOT = 'parking:lot:{lot_id}'
CACHE_KEY_LOT_SPOTS = 'parking:spots:{lot_id}'
CACHE_KEY_USER_DASHBOARD = 'user:dashboard:{user_id}'
CACHE_KEY_ADMIN_DASHBOARD = 'admin:dashboard'
CACHE_KEY_DAILY_SUMMARY = 'admin:daily_summary'
CACHE_KEY_AVAILABLE_LOTS = 'parking:available_lots'


def invalidate_lot_cache(lot_id):
    """
    Invalidate all cache related to a parking lot
    
    Args:
        lot_id: Parking lot ID
    """
    invalidate_cache(
        f'parking:lot:{lot_id}',
        f'parking:spots:{lot_id}'
    )
    invalidate_pattern('parking:lots:*')
    invalidate_pattern('parking:available_lots*')


def invalidate_user_cache(user_id):
    """
    Invalidate user dashboard cache
    
    Args:
        user_id: User ID
    """
    invalidate_cache(f'user:dashboard:{user_id}')


def invalidate_admin_dashboard_cache():
    """Invalidate admin dashboard caches"""
    invalidate_cache(
        'admin:dashboard',
        'admin:daily_summary',
        'admin:charts_data'
    )
    invalidate_pattern('admin:*')


def invalidate_all_lots_cache():
    """Invalidate all parking lots related cache"""
    invalidate_pattern('parking:*')
