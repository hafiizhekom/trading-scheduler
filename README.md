# Trading Scheduler Suite

Proyek ini terdiri dari tiga scheduler terpisah untuk mengambil data harga secara periodik: **Crypto**, **Forex**, dan **Gold**. Setiap scheduler berjalan sebagai service terpisah menggunakan Docker, mengambil data dari API eksternal, menyimpannya ke TimescaleDB, dan melakukan cache serta publikasi update ke Redis.

## Fitur Utama

- **Crypto Scheduler**: Mengambil harga cryptocurrency dari Coindesk API.
- **Forex Scheduler**: Mengambil kurs mata uang dari API forex.
- **Gold Scheduler**: Mengambil harga emas dari API eksternal.
- Penyimpanan data historis ke TimescaleDB (PostgreSQL).
- Cache harga terakhir di Redis dengan TTL.
- Publikasi update harga ke channel Redis (pub/sub).
- Scheduler otomatis setiap 1 menit.
- Mode pengembangan dengan auto-reload (watcher).

## Struktur Direktori

```
.
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

## Cara Menjalankan

### 1. Persiapan

- Pastikan Docker & Docker Compose sudah terinstal.
- Salin file `.env-example` ke masing-masing folder scheduler sebagai `.env` dan sesuaikan jika perlu.

### 2. Build & Jalankan Semua Service

```sh
docker-compose up --build
```

Service yang berjalan:
- `crypto_scheduler`: Scheduler harga crypto
- `forex_scheduler`: Scheduler kurs forex
- `gold_scheduler`: Scheduler harga emas
- `db`: TimescaleDB (PostgreSQL)
- `redis`: Redis untuk cache & pub/sub

### 3. Mode Pengembangan (Auto-reload)

Untuk mode pengembangan dengan auto-reload, jalankan watcher di masing-masing scheduler:

```sh
docker-compose run --service-ports crypto_scheduler python watcher.py
docker-compose run --service-ports forex_scheduler python watcher.py
docker-compose run --service-ports gold_scheduler python watcher.py
```

## Konfigurasi Lingkungan

Edit file `.env` di masing-masing scheduler:

- **Database**: `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`
- **API**:
  - Crypto: `COINDESK_BASE_URL`, `COINDESK_MARKET`, `SYMBOLS`
  - Forex: `FOREX_BASE_URL`, `FOREX_API_KEY`, `FOREX_SYMBOLS`
  - Gold: (disesuaikan dengan API yang digunakan)
- **Redis**: `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_TTL`, `REDIS_PUBSUB_CHANNEL`

Contoh konfigurasi dapat dilihat di [.env-example](.env-example).

## Struktur Database

- **crypto_prices**: (time, symbol, price, volume)
- **forex_rates**: (time, symbol, rate)
- **gold_prices**: (time, type_gold, sell, buy)

> **Catatan:** Pastikan tabel-tabel di atas sudah dibuat di TimescaleDB sebelum menjalankan aplikasi.

## Penjelasan Modul

- [`app/coindesk.py`](crypto_scheduler/app/coindesk.py): Fetch harga crypto dari Coindesk.
- [`app/forex.py`](forex_scheduler/app/forex.py): Fetch kurs forex dari API.
- [`app/db.py`](crypto_scheduler/app/db.py), [`forex_scheduler/app/db.py`](forex_scheduler/app/db.py), [`gold_scheduler/app/db.py`](gold_scheduler/app/db.py): Insert data ke database.
- [`app/cache.py`](crypto_scheduler/app/cache.py): Cache harga terakhir & publish ke Redis.
- [`app/scheduler.py`](crypto_scheduler/app/scheduler.py): Scheduler utama.
- `watcher.py`: Watcher untuk auto-reload saat development.

## Dependensi

Lihat `requirements.txt` di masing-masing scheduler:

- requests
- python-dotenv
- redis
- psycopg2-binary
- schedule
- watchfiles