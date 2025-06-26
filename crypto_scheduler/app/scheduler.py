from app import __init__
from app.db import insert_price
from app.coindesk import fetch_all_prices
from app.cache import get_last_price, set_last_price
import schedule, time, logging



def job():
    logging.info("Running scheduled job (batch)...")
    try:
        results = fetch_all_prices()
        for r in results:
            cache = get_last_price(r["symbol"])
            last_ts = cache.get("timestamp")
            if str(r["time"].timestamp()) == last_ts:
                logging.info(f"{r['symbol']} | Skip (same timestamp as cache)")
                continue

            insert_price(r["time"], r["symbol"], r["price"], r["volume"])
            set_last_price(r["symbol"], r["price"], r["time"].timestamp())
            logging.info(f"{r['symbol']} | {r['time']} | Price: {r['price']}")

    except Exception as e:
        logging.error(f"Fetch error: {e}")

def start_scheduler():
    logging.info("Scheduler started. Fetching every 1 minute.")
    schedule.every(10).seconds.do(job)
    job()
    while True:
        schedule.run_pending()
        time.sleep(1)
