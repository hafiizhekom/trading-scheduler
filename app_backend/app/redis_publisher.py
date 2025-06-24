import redis.asyncio as aioredis
import json
from app.models import PriceOverrideRequest

async def publish_override_to_redis(payload: PriceOverrideRequest):
    redis = aioredis.from_url("redis://redis:6379", decode_responses=True)

    if payload.type == "crypto":
        redis_key = f"override:crypto:{payload.symbol}:{payload.datetime.isoformat()}"
        redis_channel = "crypto_price_updates"
        redis_data = {
            "symbol": payload.symbol,
            "price": float(payload.custom_price),
            "time": payload.datetime.isoformat(),
            "override": True
        }

    elif payload.type == "forex":
        redis_key = f"override:forex:{payload.symbol}:{payload.datetime.isoformat()}"
        redis_channel = "forex_rate_updates"
        redis_data = {
            "symbol": payload.symbol,
            "rate": float(payload.custom_price),
            "time": payload.datetime.isoformat(),
            "override": True
        }

    elif payload.type == "gold":
        redis_key = f"override:gold:{payload.type_gold}:{payload.datetime.isoformat()}"
        redis_channel = "gold_price_updates"
        redis_data = {
            "type_gold": payload.type_gold,
            "sell": float(payload.custom_price),
            "buy": float(payload.custom_price),
            "time": payload.datetime.isoformat(),
            "override": True
        }

    await redis.set(redis_key, payload.custom_price)
    await redis.publish(redis_channel, json.dumps(redis_data))
    await redis.close()
