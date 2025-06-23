import psycopg2
import os
from dotenv import load_dotenv
from app.models import FuturePriceInput

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        dbname=os.getenv("DATABASE_NAME"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD")
    )

def insert_future_price(payload: FuturePriceInput):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO crypto_prices (time, symbol, price, volume)
                VALUES (%s, %s, %s, %s)
            """, (payload.time, payload.symbol, payload.price, None))
        conn.commit()
