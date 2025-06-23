from app import __init__
from app.db import insert_price
from app.gold import fetch_all_prices
import schedule, time, logging

def job():
    logging.info("Running scheduled job (batch)...")
    try:
        results = fetch_all_prices()
        for r in results:
            insert_price(
                time=r["time"],
                type_gold=r["type_gold"],
                sell=r["sell"],
                buy=r["buy"]
            )
            logging.info(f"{r['type_gold']} | {r['time']} | Sell: {r['sell']} | Buy: {r['buy']}")
    except Exception as e:
        logging.error(f"Fetch error: {e}")

def start_scheduler():
    logging.info("Scheduler started. Fetching every 12 PM")
    schedule.every().day.at("12:00").do(job)  # waktu dalam format HH:MM (24 jam)
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)
