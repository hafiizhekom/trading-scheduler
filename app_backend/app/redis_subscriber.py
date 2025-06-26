# app/redis_subscriber.py
import redis.asyncio as aioredis
import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
import heapq
from dateutil import parser

logger = logging.getLogger(__name__)

# Buffer per channel (pakai heapq untuk urutan otomatis)
buffers = defaultdict(list)  # channel_key -> list of (datetime, payload)

def ensure_utc(dt_raw):
    """Parse datetime dan pastikan jadi UTC."""
    dt = parser.isoparse(dt_raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt

async def buffer_append(channel_key: str, data: dict):
    try:
        time_str = data.get("time") or data.get("timestamp")
        if not time_str:
            raise ValueError("Missing time or timestamp field")
        dt = ensure_utc(time_str)
        heapq.heappush(buffers[channel_key], (dt, data))
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        logger.info(f"[BUFFER] Appended to {channel_key}: {dt.isoformat()} (now={now.isoformat()}) override={data.get('override')}")
    except Exception as e:
        logger.error(f"[BUFFER] Failed to append to buffer {channel_key}: {e}")

async def start_buffer_loop():
    while True:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)

        for channel_key in list(buffers.keys()):
            queue = buffers[channel_key]

            while queue and queue[0][0] <= now:
                dt, data = heapq.heappop(queue)

                try:
                    asset_type = data.get("asset_type", "crypto")
                    symbol = data.get("symbol") or data.get("type_gold") or "UNKNOWN"

                    from app.websocket_handler import broadcast_to_clients
                    await broadcast_to_clients(symbol, data, asset_type=asset_type)
                    logger.info(f"[BUFFER] Sent from buffer {channel_key}: {symbol} @ {dt.isoformat()}")
                except Exception as e:
                    logger.error(f"[BUFFER] Failed to send from buffer {channel_key}: {e}")

            if not queue:
                del buffers[channel_key]

        await asyncio.sleep(0.5)  # flush lebih sering untuk sinkronisasi lebih ketat

async def redis_subscriber():
    redis_client = None
    pubsub = None

    try:
        redis_client = aioredis.from_url("redis://redis:6379", decode_responses=True)
        await redis_client.ping()
        logger.info("[REDIS] Successfully connected to Redis")

        pubsub = redis_client.pubsub()

        channels = [
            "crypto_price_updates",
            "gold_price_updates",
            "forex_rate_updates"
        ]

        for channel in channels:
            await pubsub.subscribe(channel)
            logger.info(f"[REDIS] Subscribed to {channel}")

        # Start background task
        asyncio.create_task(start_buffer_loop())

        async for message in pubsub.listen():
            try:
                if message['type'] == 'message':
                    channel = message['channel']
                    logger.info(f"[REDIS] Received message from {channel}: {message['data']}")

                    data = json.loads(message['data'])

                    if channel == "crypto_price_updates":
                        symbol = data.get("symbol")
                        if symbol:
                            await buffer_append(f"crypto:{symbol}", data)

                    elif channel == "gold_price_updates":
                        await buffer_append("gold", data)

                    elif channel == "forex_rate_updates":
                        symbol = data.get("symbol") or data.get("currency")
                        if symbol:
                            await buffer_append(f"forex:{symbol}", data)

                    else:
                        logger.warning(f"[REDIS] Unknown channel: {channel}")

            except json.JSONDecodeError as e:
                logger.error(f"[REDIS] JSON decode error: {e}")
            except Exception as e:
                logger.error(f"[REDIS] Error processing message: {e}")

    except Exception as e:
        logger.error(f"[REDIS] Redis subscriber error: {e}")

    finally:
        if pubsub:
            for channel in ["crypto_price_updates", "gold_price_updates", "forex_rate_updates"]:
                await pubsub.unsubscribe(channel)
            await pubsub.close()
        if redis_client:
            await redis_client.close()
        logger.info("[REDIS] Redis connection closed")
