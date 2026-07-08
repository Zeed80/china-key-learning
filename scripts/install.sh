#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="auto"
START_SERVICES="1"
ENABLE_AUTOSTART="0"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin12345}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
HOST_IP="${HOST_IP:-localhost}"

usage() {
  cat <<'USAGE'
China Key Learning installer

Usage:
  ./scripts/install.sh [--docker|--local] [--no-start] [--autostart]

Environment:
  ADMIN_EMAIL       Admin user email. Default: admin@example.com
  ADMIN_PASSWORD    Admin user password. Default: admin12345
  BACKEND_PORT      Backend port for local mode. Default: 8001
  FRONTEND_PORT     Frontend port for local mode. Default: 5173
  HOST_IP           Public host/IP for Docker and local mode. Default: localhost
  SECRET_KEY        Backend secret key for Docker mode. Default: change-me-before-public-use

Examples:
  ./scripts/install.sh --docker
  ./scripts/install.sh --docker --autostart
  ADMIN_PASSWORD='change-me' ./scripts/install.sh --local
  ./scripts/install.sh --local --no-start
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --docker)
      MODE="docker"
      ;;
    --local)
      MODE="local"
      ;;
    --no-start)
      START_SERVICES="0"
      ;;
    --autostart)
      ENABLE_AUTOSTART="1"
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
  shift
done

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing dependency: $1" >&2
    return 1
  fi
}

detect_mode() {
  if [ "$MODE" != "auto" ]; then
    return
  fi
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    MODE="docker"
  else
    MODE="local"
  fi
}

install_docker() {
  need_cmd docker
  docker compose version >/dev/null
  cd "$ROOT_DIR"
  ADMIN_EMAIL="$ADMIN_EMAIL" ADMIN_PASSWORD="$ADMIN_PASSWORD" HOST_IP="$HOST_IP" docker compose -f infra/docker-compose.yml build
  if [ "$START_SERVICES" = "1" ]; then
    ADMIN_EMAIL="$ADMIN_EMAIL" ADMIN_PASSWORD="$ADMIN_PASSWORD" HOST_IP="$HOST_IP" docker compose -f infra/docker-compose.yml up -d
    echo
    echo "Started with Docker Compose:"
    echo "  Frontend: http://${HOST_IP}:5173"
    echo "  Backend:  http://${HOST_IP}:8001"
  else
    echo "Docker images built. Start later with:"
    echo "  ADMIN_EMAIL='$ADMIN_EMAIL' ADMIN_PASSWORD='***' HOST_IP='$HOST_IP' docker compose -f infra/docker-compose.yml up -d"
  fi

  if [ "$ENABLE_AUTOSTART" = "1" ]; then
    ADMIN_EMAIL="$ADMIN_EMAIL" ADMIN_PASSWORD="$ADMIN_PASSWORD" HOST_IP="$HOST_IP" START_NOW="$START_SERVICES" "$ROOT_DIR/scripts/install-autostart.sh"
  fi
}

install_local() {
  if [ "$ENABLE_AUTOSTART" = "1" ]; then
    echo "--autostart is supported only with --docker. Local mode uses foreground dev services." >&2
    exit 2
  fi

  need_cmd python3
  need_cmd npm
  cd "$ROOT_DIR"

  if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
  fi

  python3 -m venv backend/.venv
  backend/.venv/bin/pip install --upgrade pip
  backend/.venv/bin/pip install -r backend/requirements.txt

  cd "$ROOT_DIR/frontend"
  if [ -f package-lock.json ]; then
    npm ci
  else
    npm install
  fi
  npm run build

  cd "$ROOT_DIR/backend"
  .venv/bin/python -m app.db.seed --admin-email "$ADMIN_EMAIL" --admin-password "$ADMIN_PASSWORD"
  .venv/bin/python -m app.db.content_audit

  if [ "$START_SERVICES" = "1" ]; then
    mkdir -p "$ROOT_DIR/.runtime"
    if [ -f "$ROOT_DIR/.runtime/backend.pid" ]; then
      old_backend="$(cat "$ROOT_DIR/.runtime/backend.pid" 2>/dev/null || true)"
      if [ -n "$old_backend" ] && kill -0 "$old_backend" 2>/dev/null; then
        kill "$old_backend" || true
      fi
    fi
    if [ -f "$ROOT_DIR/.runtime/frontend.pid" ]; then
      old_frontend="$(cat "$ROOT_DIR/.runtime/frontend.pid" 2>/dev/null || true)"
      if [ -n "$old_frontend" ] && kill -0 "$old_frontend" 2>/dev/null; then
        kill "$old_frontend" || true
      fi
    fi

    cd "$ROOT_DIR/backend"
    CORS_ORIGINS="http://localhost:${FRONTEND_PORT},http://127.0.0.1:${FRONTEND_PORT},http://${HOST_IP}:${FRONTEND_PORT}" \
      .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" >"$ROOT_DIR/.runtime/backend.log" 2>&1 &
    echo "$!" > "$ROOT_DIR/.runtime/backend.pid"

    cd "$ROOT_DIR/frontend"
    VITE_API_URL="http://${HOST_IP}:${BACKEND_PORT}" \
      npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" >"$ROOT_DIR/.runtime/frontend.log" 2>&1 &
    echo "$!" > "$ROOT_DIR/.runtime/frontend.pid"

    echo
    echo "Started local services:"
    echo "  Frontend: http://${HOST_IP}:${FRONTEND_PORT}"
    echo "  Backend:  http://${HOST_IP}:${BACKEND_PORT}"
    echo "  Logs:     .runtime/backend.log and .runtime/frontend.log"
  else
    echo "Local dependencies installed and database seeded."
  fi
}

detect_mode
case "$MODE" in
  docker)
    install_docker
    ;;
  local)
    install_local
    ;;
  *)
    echo "Invalid mode: $MODE" >&2
    exit 2
    ;;
esac
