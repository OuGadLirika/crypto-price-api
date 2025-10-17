# Crypto Price API

Async REST API for live crypto prices from KuCoin, with PostgreSQL storage.

## Features
- Get current price for any currency
- View and clear price history
- Health and metrics endpoints
- Docker and local run support
- Swagger API docs

## Endpoints
| Method | Path                    | Description                |
|--------|-------------------------|----------------------------|
| GET    | /price/{currency}       | Get current price          |
| GET    | /price/history?page=1   | Paginated price history    |
| DELETE | /price/history          | Delete all history         |
| GET    | /health                 | Health check               |
| GET    | /metrics                | App metrics                |

Swagger UI: http://localhost:8000/docs

## Quick Start
**Docker:**
```bash
docker-compose up --build
```
**Local:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # or .venv/bin/activate.fish
pip install -r requirements.txt
docker-compose up -d db
set -x DATABASE_URL "postgresql://qorpo_user:qorpo_password@localhost:5432/qorpo"
alembic upgrade head
set -x DATABASE_URL "postgresql+asyncpg://qorpo_user:qorpo_password@localhost:5432/qorpo"
python -m app.main
```

## Example
```bash
curl http://localhost:8000/price/BTC
```

## Testing
```bash
pytest tests/ -v
```

## Env Vars
- DATABASE_URL
- HOST / PORT
- PAGE_SIZE
- ENABLE_UVLOOP