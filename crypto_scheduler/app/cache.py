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
REDIS_CHANNEL = os.getenv("REDIS_PUBSUB_CHANNEL", "crypto_price_updates")

rds = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_last_price(symbol):
    key = f"crypto_price:{symbol}"
    return rds.hgetall(key)  # {'price': ..., 'timestamp': ...}

def set_last_price(symbol, price, timestamp):
    key = f"crypto_price:{symbol}"
    payload = {
        "symbol": symbol,
        "price": price,
        # "timestamp": str(timestamp),
        "time": datetime.utcfromtimestamp(timestamp).isoformat(),
        "asset_type": "crypto"
    }
    rds.hset(key, mapping={"price": price, "timestamp": timestamp})
    rds.expire(key, REDIS_TTL)  # ✅ TTL dalam detik
    rds.publish(REDIS_CHANNEL, json.dumps(payload))
