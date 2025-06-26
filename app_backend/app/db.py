import psycopg2
import os
from dotenv import load_dotenv
from app.models import PriceOverrideRequest

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
    )
    
def get_crypto_history(symbol):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                TO_CHAR(COALESCE(o.time, c.time), 'YYYY-MM-DD"T"HH24:MI:SS.US') AS time,
                c.symbol,
                COALESCE(o.price, c.price) AS price,
                CASE WHEN o.price IS NOT NULL THEN TRUE ELSE FALSE END AS override
            FROM crypto_prices c
            LEFT JOIN LATERAL (
                SELECT * FROM crypto_price_overrides o
                WHERE o.symbol = c.symbol AND o.time = c.time
                LIMIT 1
            ) o ON TRUE
            WHERE c.symbol = %s
            ORDER BY time ASC
        """, (symbol,))
        cols = [desc[0] for desc in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return rows
    finally:
        cur.close()
        conn.close()


def get_forex_history(symbol):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                TO_CHAR(COALESCE(o.time, f.time), 'YYYY-MM-DD"T"HH24:MI:SS.US') AS time,
                f.symbol,
                COALESCE(o.rate, f.rate) AS rate,
                CASE WHEN o.rate IS NOT NULL THEN TRUE ELSE FALSE END AS override
            FROM forex_rates f
            LEFT JOIN LATERAL (
                SELECT * FROM forex_rate_overrides o
                WHERE o.symbol = f.symbol AND o.time = f.time
                LIMIT 1
            ) o ON TRUE
            WHERE f.symbol = %s
            ORDER BY time ASC
        """, (symbol,))
        cols = [desc[0] for desc in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return rows
    finally:
        cur.close()
        conn.close()


def get_gold_history(type_gold):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                FLOOR(EXTRACT(EPOCH FROM COALESCE(o.time, g.time))) AS time,
                g.type_gold,
                COALESCE(o.sell, g.sell) AS sell,
                COALESCE(o.buy, g.buy) AS buy,
                CASE WHEN o.sell IS NOT NULL OR o.buy IS NOT NULL THEN TRUE ELSE FALSE END AS override
            FROM gold_prices g
            LEFT JOIN LATERAL (
                SELECT * FROM gold_price_overrides o
                WHERE o.type_gold = g.type_gold AND o.time = g.time
                LIMIT 1
            ) o ON TRUE
            WHERE g.type_gold = %s
            ORDER BY time ASC
        """, (type_gold,))
        cols = [desc[0] for desc in cur.description]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
        return rows
    finally:
        cur.close()
        conn.close()


def insert_override_to_db(payload: PriceOverrideRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if payload.type == "crypto":
            cur.execute("""
                INSERT INTO crypto_price_overrides (time, symbol, price, id_user)
                VALUES (%s, %s, %s, %s)
            """, (payload.datetime, payload.symbol, payload.custom_price, payload.id_user))

        elif payload.type == "forex":
            cur.execute("""
                INSERT INTO forex_rate_overrides (time, symbol, rate, id_user)
                VALUES (%s, %s, %s, %s)
            """, (payload.datetime, payload.symbol, payload.custom_price, payload.id_user))

        elif payload.type == "gold":
            cur.execute("""
                INSERT INTO gold_price_overrides (time, type_gold, sell, buy, id_user)
                VALUES (%s, %s, %s, %s, %s)
            """, (payload.datetime, payload.type_gold, payload.custom_price, payload.custom_price, payload.id_user))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()
