# app/redis_subscriber.py
import redis.asyncio as aioredis
import asyncio
import json
import logging
from app.websocket_handler import broadcast_crypto_price, broadcast_gold_price, broadcast_forex_rate

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
        
        # Subscribe to different channels
        channels = [
            "crypto_price_updates",  # For crypto prices
            "gold_price_updates",    # For gold prices  
            "forex_rate_updates"     # For forex rates
        ]
        
        for channel in channels:
            await pubsub.subscribe(channel)
            logger.info(f"[REDIS] Subscribed to {channel}")

        async for message in pubsub.listen():
            try:
                if message['type'] == 'message':
                    channel = message['channel']
                    logger.info(f"[REDIS] Received message from {channel}: {message['data']}")
                    
                    data = json.loads(message['data'])
                    
                    # Route to appropriate broadcast function based on channel
                    if channel == "crypto_price_updates":
                        symbol = data.get("symbol")
                        if symbol:
                            await broadcast_crypto_price(symbol, data)
                            logger.info(f"[REDIS] Broadcasted crypto data for {symbol}")
                        
                    elif channel == "gold_price_updates":
                        await broadcast_gold_price(data)
                        logger.info("[REDIS] Broadcasted gold price data")
                        
                    elif channel == "forex_rate_updates":
                        symbol = data.get("symbol") or data.get("currency")
                        if symbol:
                            await broadcast_forex_rate(symbol, data)
                            logger.info(f"[REDIS] Broadcasted forex data for {symbol}")
                    
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