import redis
from app.core.config import settings

def get_redis():
    r = redis.from_url(settings.get_redis_url, decode_responses=True)
    try:
        yield r
    finally:
        r.close()
