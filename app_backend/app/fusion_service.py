# fusion_service.py
# Menggabungkan data scheduler dan override dari PostgreSQL dan Redis

import redis.asyncio as aioredis
from psycopg2.extras import RealDictCursor
from datetime import datetime
from app.db import get_connection
import json

async def get_effective_price(source: str, symbol: str = None, type_gold: str = None, at_time: datetime = None):
    """
    source: "crypto", "forex", "gold"
    symbol: untuk crypto/forex
    type_gold: untuk gold
    at_time: waktu target
    """
    redis = aioredis.from_url("redis://redis:6379", decode_responses=True)
    try:
        redis_key = None

        if source == "crypto":
            redis_key = f"override:crypto:{symbol}:{at_time.isoformat()}"
        elif source == "forex":
            redis_key = f"override:forex:{symbol}:{at_time.isoformat()}"
        elif source == "gold":
            redis_key = f"override:gold:{type_gold}:{at_time.isoformat()}"

        if redis_key:
            override_value = await redis.get(redis_key)
            if override_value is not None:
                return float(override_value), True  # true = from override
    finally:
        await redis.close()

    # Kalau tidak ada di Redis, fallback ke DB asli
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if source == "crypto":
            cur.execute("""
                SELECT price FROM crypto_prices
                WHERE symbol = %s AND time = %s
                LIMIT 1
            """, (symbol, at_time))
        elif source == "forex":
            cur.execute("""
                SELECT rate FROM forex_rates
                WHERE symbol = %s AND time = %s
                LIMIT 1
            """, (symbol, at_time))
        elif source == "gold":
            cur.execute("""
                SELECT sell FROM gold_prices
                WHERE type_gold = %s AND time = %s
                LIMIT 1
            """, (type_gold, at_time))

        row = cur.fetchone()
        if row:
            return float(list(row.values())[0]), False
        return None, False
    finally:
        cur.close()
        conn.close()
