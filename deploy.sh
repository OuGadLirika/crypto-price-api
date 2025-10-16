#!/usr/bin/env bash
set -e

echo "╔═══════════════════════════════════════════╗"
echo "║  Qorpo Crypto API - Quick Deploy         ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not installed"
    exit 1
fi

echo "✅ Docker available"
echo ""
echo "Choose mode:"
echo "1) Docker: Everything in Docker"
echo "2) Local: App locally + PostgreSQL in Docker"
echo ""
read -p "Choice (1 or 2): " choice

case $choice in
  1)
    echo "🚀 Docker mode..."
    docker-compose down -v 2>/dev/null || true
    docker-compose up -d --build
    COMPOSE_FILE="docker-compose.yml"
    ;;
  2)
    echo "🧰 Local mode..."

    if ! command -v python3 &> /dev/null; then
      echo "❌ Python3 not found"
      exit 1
    fi

    if [ ! -d ".venv" ]; then
      echo "📦 Creating .venv..."
      python3 -m venv .venv
    fi

    echo "📦 Installing dependencies..."
    . .venv/bin/activate
    pip install --upgrade pip >/dev/null
    pip install -r requirements.txt

    echo "🐘 Starting PostgreSQL..."
    docker-compose up -d db

    echo "🔧 Running migrations..."
    docker-compose run --rm migration alembic upgrade head

    echo "🚀 Starting app..."
    python -m app.main

    echo "🛑 Stop DB: docker-compose down"
    exit 0
    ;;
  *)
    echo "❌ Invalid choice"
    exit 1
    ;;
esac

echo "⏳ Waiting for services..."
sleep 3

if ! docker-compose -f $COMPOSE_FILE ps | grep -q "Up"; then
  echo "❌ Services failed to start"
  docker-compose -f $COMPOSE_FILE logs
  exit 1
fi

echo ""
echo "✅ Deployed!"
echo ""
echo "API:     http://localhost:8000"
echo "Swagger: http://localhost:8000/docs"
echo ""
echo "Test:"
echo "  curl http://localhost:8000/price/BTC"
echo "  curl http://localhost:8000/price/history?page=1"
echo ""
echo "Stop: docker-compose down"
