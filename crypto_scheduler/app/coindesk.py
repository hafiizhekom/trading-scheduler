import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("COINDESK_BASE_URL").rstrip("/")
MARKET = os.getenv("COINDESK_MARKET", "cadli")
SYMBOLS = os.getenv("SYMBOLS", "").split(",")

def fetch_all_prices():
    instruments = ",".join(SYMBOLS)
    url = f"{BASE_URL}/latest/tick?market={MARKET}&instruments={instruments}&apply_mapping=true"
    logging.info(f"Fetching from: {url}")

    resp = requests.get(url)
    logging.debug(f"Raw response: {resp.text}")
    resp.raise_for_status()

    result = []
    payload = resp.json()
    data = payload.get("Data", {})
    err = payload.get("Err", {})

    if err:
        logging.warning(f"API Error: {err}")
        return []

    for symbol, entry in data.items():
        ts = entry.get("VALUE_LAST_UPDATE_TS")
        price = entry.get("VALUE")
        volume = entry.get("LAST_UPDATE_QUOTE_QUANTITY")
        if ts and price:
            dt = datetime.utcfromtimestamp(ts)
            result.append({
                "time": dt,
                "symbol": symbol,
                "price": float(price),
                "volume": float(volume) if volume else None
            })
        else:
            logging.warning(f"{symbol} missing price or timestamp")

    return result
