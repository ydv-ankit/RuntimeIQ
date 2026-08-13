from redis import Redis

def get_redis_connection():
    try:
        return Redis(
            host="localhost",
            port=6379,
            db=0,
            password=None
        )
    except Exception as e:
        print("redis connection error", e)