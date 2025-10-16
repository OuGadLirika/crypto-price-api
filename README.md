# Qorpo Crypto Price API

REST API with **aiohttp** + **asyncio** + **ccxt** + **SQLAlchemy** + **PostgreSQL**

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/price/{currency}` | Fetch KuCoin bid price for `{currency}/USDT`, save to DB |
| `GET` | `/price/history?page=1` | Paginated history (10 per page) |
| `DELETE` | `/price/history` | Delete all records |

**Swagger UI**: http://localhost:8000/docs

## Quick Start

```bash
./deploy.sh
```

Choose mode:
- **1** - Docker (all-in-one)
- **2** - Local app + Docker DB

## Manual Start

### Docker
```bash
docker-compose up -d
```

### Local
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker-compose up -d db
alembic upgrade head
python -m app.main
```

### Gunicorn
```bash
gunicorn -c gunicorn.conf.py app.wsgi:app
```

## Tests

```bash
pytest
```
