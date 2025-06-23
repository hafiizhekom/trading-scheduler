import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("FOREX_BASE_URL").rstrip("/")
API_KEY = os.getenv("FOREX_API_KEY")
SYMBOLS = os.getenv("FOREX_SYMBOLS", "").split(",")

def fetch_all_prices():
    url = f"{BASE_URL}?access_key={API_KEY}"
    logging.info(f"Fetching from: {url}")

    resp = requests.get(url)
    logging.debug(f"Raw response: {resp.text}")
    resp.raise_for_status()

    payload = resp.json()
    rates = payload.get("rates", {})
    ts = payload.get("timestamp")

    if not rates or not ts:
        logging.warning("Empty rates or missing timestamp")
        return []

    dt = datetime.utcfromtimestamp(ts)
    result = []

    for symbol in SYMBOLS:
        rate = rates.get(symbol)
        if rate is not None:
            result.append({
                "time": dt,
                "symbol": symbol.upper(),
                "rate": float(rate)
            })
        else:
            logging.warning(f"Symbol '{symbol}' not found in rates.")

    return result
