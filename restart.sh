#!/usr/bin/env bash
# ==============================================================================
# ALHSI Restart Script
# Restarts the application cleanly in Docker (default) or locally.
# Usage:
#   ./restart.sh          # Build & run inside Docker container
#   ./restart.sh --local  # Restart native local Python process
#   ./restart.sh --test   # Run test suite inside Docker container
# ==============================================================================

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

PORT=8000
MODE="docker"

for arg in "$@"; do
  case $arg in
    --local)
      MODE="local"
      shift
      ;;
    --test)
      MODE="test"
      shift
      ;;
    --docker)
      MODE="docker"
      shift
      ;;
  esac
done

echo "================================================================="
echo "   ALHSI: Agent Loop Harness Self-Improvement System            "
echo "================================================================="

# ------------------------------------------------------------------------------
# 1. Clean up existing processes / containers on port 8000
# ------------------------------------------------------------------------------
echo "[-] Checking for running instances on port ${PORT}..."

# Stop and remove existing docker container if present (running, stopped, or created)
if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
  echo "[-] Cleaning up any existing Docker container 'alhsi-app'..."
  docker rm -f alhsi-app >/dev/null 2>&1 || true
fi

# Stop any local process occupying port 8000
LOCAL_PID=$(lsof -ti :${PORT} 2>/dev/null || true)
if [ -n "$LOCAL_PID" ]; then
  echo "[-] Terminating local process PID ${LOCAL_PID} on port ${PORT}..."
  kill -9 $LOCAL_PID 2>/dev/null || true
  sleep 1
fi

# ------------------------------------------------------------------------------
# 2. Execute selected mode
# ------------------------------------------------------------------------------
if [ "$MODE" = "test" ]; then
  echo "[+] Running ALHSI test suite inside Docker..."
  docker build -t alhsi:latest .
  docker run --rm alhsi:latest pytest -v
  echo "[✓] All tests passed inside Docker!"
  exit 0
fi

if [ "$MODE" = "local" ]; then
  echo "[+] Starting ALHSI locally in background..."
  nohup python3 -m alhsi serve --port ${PORT} > /tmp/alhsi_local.log 2>&1 &
  NEW_PID=$!
  echo "[+] Local server started with PID ${NEW_PID}. Waiting for healthcheck..."
  
  for i in {1..15}; do
    if curl -s "http://127.0.0.1:${PORT}/api/state" >/dev/null 2>&1; then
      echo "[✓] ALHSI is healthy and running locally at http://localhost:${PORT}"
      echo "[i] View logs at: /tmp/alhsi_local.log"
      exit 0
    fi
    sleep 1
  done
  echo "[!] Local server failed to respond within 15 seconds. Check /tmp/alhsi_local.log"
  exit 1
fi

# Default: Docker mode
if ! command -v docker >/dev/null 2>&1 || ! docker info >/dev/null 2>&1; then
  echo "[!] Docker daemon is not running or docker CLI not found."
  echo "[!] Falling back to local mode..."
  exec "$0" --local
fi

echo "[+] Building Docker image (alhsi:latest)..."
docker build -t alhsi:latest .

echo "[+] Launching container 'alhsi-app' on port ${PORT}..."
docker rm -f alhsi-app >/dev/null 2>&1 || true
docker run -d \
  --name alhsi-app \
  -p ${PORT}:${PORT} \
  --restart unless-stopped \
  -e PYTHONUNBUFFERED=1 \
  -e PYTHONDONTWRITEBYTECODE=1 \
  alhsi:latest

echo "[+] Waiting for container health check..."
SUCCESS=0
for i in {1..20}; do
  if curl -s "http://localhost:${PORT}/api/state" >/dev/null 2>&1; then
    SUCCESS=1
    break
  fi
  sleep 1
  printf "."
done
echo ""

if [ $SUCCESS -eq 1 ]; then
  echo "================================================================="
  echo " [✓] ALHSI is LIVE and running inside Docker container!         "
  echo "     Dashboard: http://localhost:${PORT}                        "
  echo "     Container: alhsi-app (Docker)                              "
  echo "     View logs: docker logs -f alhsi-app                        "
  echo "     Stop:      docker stop alhsi-app                           "
  echo "================================================================="
else
  echo "[!] Container started but healthcheck failed. Container logs:"
  docker logs alhsi-app
  exit 1
fi
