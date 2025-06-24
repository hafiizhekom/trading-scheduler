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
