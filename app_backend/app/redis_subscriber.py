# app/redis_subscriber.py
import redis.asyncio as aioredis
import asyncio
import json
import logging
from app.websocket_handler import broadcast_to_clients

logger = logging.getLogger(__name__)

async def redis_subscriber():
    redis_client = None
    pubsub = None
    
    try:
        # Connect to Redis
        redis_client = aioredis.from_url("redis://redis:6379", decode_responses=True)
        
        # Test connection
        await redis_client.ping()
        logger.info("[REDIS] Successfully connected to Redis")
        
        pubsub = redis_client.pubsub()
        await pubsub.subscribe("crypto_price_updates")
        logger.info("[REDIS] Subscribed to crypto_price_updates channel")

        async for message in pubsub.listen():
            try:
                if message['type'] == 'message':
                    logger.info(f"[REDIS] Received message: {message['data']}")
                    
                    data = json.loads(message['data'])
                    symbol = data.get("symbol")
                    
                    if symbol:
                        await broadcast_to_clients(symbol, data)
                        logger.info(f"[REDIS] Broadcasted data for {symbol}")
                    else:
                        logger.warning(f"[REDIS] No symbol in message: {data}")
                        
            except json.JSONDecodeError as e:
                logger.error(f"[REDIS] JSON decode error: {e}")
            except Exception as e:
                logger.error(f"[REDIS] Error processing message: {e}")
                
    except Exception as e:
        logger.error(f"[REDIS] Redis subscriber error: {e}")
        
    finally:
        if pubsub:
            await pubsub.unsubscribe("crypto_price_updates")
            await pubsub.close()
        if redis_client:
            await redis_client.close()
        logger.info("[REDIS] Redis connection closed")