#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "[FAIL] Docker chưa được cài hoặc không có trong PATH"
  exit 1
fi

echo "[OK] Docker command available"
if ! docker info >/dev/null 2>&1; then
  echo "[FAIL] Docker daemon chưa chạy"
  exit 1
fi

echo "[OK] Docker daemon is running"

if [[ ! -f .env ]]; then
  echo "[FAIL] Thiếu file .env (hãy copy từ .env.example)"
  exit 1
fi

echo "[OK] .env exists"

required=(SECRET_KEY DATABASE_URL OPENAI_MODEL CV_UPLOAD_DIR JD_UPLOAD_DIR EXPORTS_DIR)
for key in "${required[@]}"; do
  if ! grep -q "^${key}=" .env; then
    echo "[FAIL] Thiếu biến ${key} trong .env"
    exit 1
  fi
done

echo "[OK] Required env keys exist"

mkdir -p data/uploads/cv data/uploads/jd data/exports

echo "[OK] data directories ready"

echo "[INFO] Checking DB container status (if compose already up)..."
if docker compose ps db 2>/dev/null | grep -q "Up"; then
  echo "[OK] DB container is up"
else
  echo "[WARN] DB container chưa chạy (hãy chạy: docker compose up -d)"
fi

