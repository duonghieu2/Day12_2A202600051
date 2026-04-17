import time
import redis
from fastapi import HTTPException
from app.config import settings

def get_redis_client():
    if not settings.redis_url:
        raise ValueError("REDIS_URL must be configured")
    # Tries to parse the redis url and return a client
    return redis.from_url(settings.redis_url)

r = None
try:
    if settings.redis_url:
        r = get_redis_client()
except Exception as e:
    import logging
    logging.getLogger(__name__).warning("Could not connect to Redis: %s", e)

def check_rate_limit(user_id: str):
    """
    Check if the user has exceeded their rate limit using a sliding window algorithm in Redis.
    """
    if not r:
        return # Skip rate limiting if no redis client
    
    current_time_float = time.time()
    window_start = current_time_float - 60
    
    key = f"rate_limit:{user_id}"
    
    pipeline = r.pipeline()
    # Remove timestamps older than 60 seconds
    pipeline.zremrangebyscore(key, '-inf', window_start)
    # Add current timestamp
    pipeline.zadd(key, {f"{current_time_float}:{user_id}": current_time_float})
    # Count requests in the current window
    pipeline.zcard(key)
    # Set expiration on the key
    pipeline.expire(key, 60)
    
    results = pipeline.execute()
    request_count = results[2]
    
    if request_count > settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": "60"},
        )
