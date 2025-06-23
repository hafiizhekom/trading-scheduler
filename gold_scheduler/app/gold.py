import os
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("GOLD_BASE_URL").rstrip("/")

def fetch_all_prices():
    url = f"{BASE_URL}"
    logging.info(f"Fetching from: {url}")

    resp = requests.get(url)
    logging.debug(f"Raw response: {resp.text}")
    resp.raise_for_status()
    
    payload = resp.json()
    data = payload.get("data", {})

    if not isinstance(data, list):
        logging.warning("Unexpected response format, 'data' is not a list.")
        return []

    now = datetime.utcnow()
    result = []

    for item in data:
        try:
            result.append({
                "time": now,
                "type_gold": item["type"].upper(),  # ANTAM
                "sell": float(item["sell"]),
                "buy": float(item["buy"])
            })
        except Exception as e:
            logging.warning(f"Failed to parse item {item}: {e}")
            continue

    return result
