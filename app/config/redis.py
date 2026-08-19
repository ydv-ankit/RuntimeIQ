from redis.asyncio import Redis
from app.config.env import settings

def get_redis_connection():
    try:
        return Redis(
            host = settings.REDIS_HOST,
            port = settings.REDIS_PORT,
            db = 0,
            socket_timeout = None,
            socket_connect_timeout = 5,
        )
    except Exception as e:
        print("redis connection error", e)
