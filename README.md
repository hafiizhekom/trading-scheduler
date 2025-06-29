# Trading Scheduler Suite

Trading Scheduler Suite is an integrated system consisting of three separate schedulers for periodically fetching price data: **Crypto**, **Forex**, and **Gold**. Each scheduler runs as a separate service using Docker, fetches data from external APIs, stores it in TimescaleDB, and handles caching and price update publishing to Redis. There is also a FastAPI backend for API and WebSocket access.

## Main Features

- **Crypto Scheduler**: Fetches cryptocurrency prices from APIs (e.g., Coindesk).
- **Forex Scheduler**: Fetches foreign exchange rates from forex APIs.
- **Gold Scheduler**: Fetches gold prices from external APIs.
- Stores historical data in TimescaleDB (PostgreSQL).
- Caches the latest prices in Redis with TTL.
- Publishes price updates to Redis channels (pub/sub).
- Automatic scheduler (default: every 1 minute, configurable).
- Development mode with auto-reload (watcher).
- FastAPI backend for API, WebSocket, and price override.

## Directory Structure

```
.
├── app_backend/
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── crypto_scheduler/
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── forex_scheduler/
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── gold_scheduler/
│   ├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
├── docker-compose.yml
├── .env-example
├── .gitignore
└── README.md
```

## How to Run

### 1. Preparation

- Make sure Docker & Docker Compose are installed.
- Copy the `.env-example` file to each scheduler and backend folder as `.env`, then adjust the configuration as needed.

### 2. Build & Run All Services

```sh
docker-compose up --build
```

Services that will run:
- `crypto_scheduler`: Crypto price scheduler
- `forex_scheduler`: Forex rate scheduler
- `gold_scheduler`: Gold price scheduler
- `app_backend`: FastAPI backend (API & WebSocket)
- `db`: TimescaleDB (PostgreSQL)
- `redis`: Redis for cache & pub/sub

### 3. Development Mode (Auto-reload)

For development mode with auto-reload, run the watcher in each scheduler/backend:

```sh
docker-compose run --service-ports crypto_scheduler python watcher.py
docker-compose run --service-ports forex_scheduler python watcher.py
docker-compose run --service-ports gold_scheduler python watcher.py
docker-compose run --service-ports app_backend python watcher.py
```

## Environment Configuration

Edit the `.env` file in each scheduler/backend:

- **Database**: `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`
- **API**:
  - Crypto: `COINDESK_BASE_URL`, `COINDESK_MARKET`, `SYMBOLS`
  - Forex: `FOREX_BASE_URL`, `FOREX_API_KEY`, `FOREX_SYMBOLS`
  - Gold: `GOLD_BASE_URL`, etc.
- **Redis**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_TTL`, `REDIS_PUBSUB_CHANNEL`

See [.env-example](.env-example) for configuration examples.

## Database Structure

- **crypto_prices**: (time, symbol, price, volume)
- **forex_rates**: (time, symbol, rate)
- **gold_prices**: (time, type_gold, sell, buy)
- **crypto_price_overrides**, **forex_rate_overrides**, **gold_price_overrides**: for price override features

> **Note:** Make sure the tables above are created in TimescaleDB before running the application.

## Module Overview

- [`crypto_scheduler/app/coindesk.py`](crypto_scheduler/app/coindesk.py): Fetches crypto prices from API.
- [`forex_scheduler/app/forex.py`](forex_scheduler/app/forex.py): Fetches forex rates from API.
- [`gold_scheduler/app/gold.py`](gold_scheduler/app/gold.py): Fetches gold prices from API.
- [`*_scheduler/app/db.py`](crypto_scheduler/app/db.py), [`forex_scheduler/app/db.py`](forex_scheduler/app/db.py), [`gold_scheduler/app/db.py`](gold_scheduler/app/db.py): Inserts data into the database.
- [`*_scheduler/app/cache.py`](crypto_scheduler/app/cache.py), etc.: Caches the latest prices & publishes to Redis.
- [`*_scheduler/app/scheduler.py`](crypto_scheduler/app/scheduler.py), etc.: Main scheduler.
- [`app_backend/app/`](app_backend/app/): FastAPI backend (API, WebSocket, override, etc.).
- `watcher.py`: Watcher for auto-reload during development.

## Dependencies

See `requirements.txt` in each scheduler and backend:

- requests
- python-dotenv
- redis
- psycopg2-binary
- schedule
- watchfiles
- fastapi, uvicorn (backend)