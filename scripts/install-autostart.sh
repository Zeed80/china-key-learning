#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="${SERVICE_NAME:-china-key-learning}"
ENV_FILE="$ROOT_DIR/.runtime/docker.env"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@example.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-admin12345}"
SECRET_KEY="${SECRET_KEY:-change-me-before-public-use}"
HOST_IP="${HOST_IP:-localhost}"
START_NOW="${START_NOW:-1}"

need_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing dependency: $1" >&2
    exit 1
  fi
}

need_cmd docker
need_cmd systemctl

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin is not available." >&2
  exit 1
fi

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  need_cmd sudo
  SUDO="sudo"
fi

DOCKER_BIN="$(command -v docker)"
SYSTEMD_UNIT="/etc/systemd/system/${SERVICE_NAME}.service"

mkdir -p "$ROOT_DIR/.runtime"
umask 077
cat > "$ENV_FILE" <<EOF
ADMIN_EMAIL=${ADMIN_EMAIL}
ADMIN_PASSWORD=${ADMIN_PASSWORD}
SECRET_KEY=${SECRET_KEY}
HOST_IP=${HOST_IP}
VITE_API_URL=http://${HOST_IP}:8001
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://${HOST_IP}:5173
EOF

tmp_unit="$(mktemp)"
cat > "$tmp_unit" <<EOF
[Unit]
Description=China Key Learning Docker Compose stack
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${ROOT_DIR}
ExecStart=${DOCKER_BIN} compose -f infra/docker-compose.yml --env-file ${ENV_FILE} up -d
ExecStop=${DOCKER_BIN} compose -f infra/docker-compose.yml --env-file ${ENV_FILE} down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

$SUDO install -m 0644 "$tmp_unit" "$SYSTEMD_UNIT"
rm -f "$tmp_unit"

$SUDO systemctl daemon-reload
if [ "$START_NOW" = "1" ]; then
  $SUDO systemctl enable --now "${SERVICE_NAME}.service"
else
  $SUDO systemctl enable "${SERVICE_NAME}.service"
fi

echo "Installed systemd autostart unit: ${SERVICE_NAME}.service"
echo "Status: systemctl status ${SERVICE_NAME}.service"
