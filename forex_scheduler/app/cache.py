import redis
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TTL = int(os.getenv("REDIS_TTL", 60))
REDIS_CHANNEL = os.getenv("REDIS_PUBSUB_CHANNEL", "forex_rate_updates")

rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_last_price(symbol):
    key = f"forex_rate:{symbol}"
    return rds.hgetall(key)  # {'price': ..., 'timestamp': ...}

def set_last_price(symbol, rate, timestamp):
    key = f"forex_rate:{symbol}"
    payload = {
        "symbol": symbol,
        "rate": rate,
        # "timestamp": str(timestamp),
        "time": datetime.utcfromtimestamp(timestamp).isoformat(),
        "asset_type": "forex"
    }
    rds.hset(key, mapping={"rate": rate, "timestamp": timestamp})
    rds.expire(key, REDIS_TTL)  # ✅ TTL dalam detik
    rds.publish(REDIS_CHANNEL, json.dumps(payload))
