from enum import Enum

class RedisEnums(Enum):
    RUN_QUEUE_KEY = "run:queue"             # list
    RUN_LEASE_KEY = "run:leases"            # sorted set
    RUN_LEASE_OWNERS_KEY = "run:lease:owners"     # hash

LEASE_TIME = 20                             # 60 seconds