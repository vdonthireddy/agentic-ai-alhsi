#!/usr/bin/env bash
# Quickstart script for ALHSI (Agent Loop Harness Self-Improvement)

set -e

PORT=${1:-8000}
HOST="127.0.0.1"

echo "================================================================="
echo "   ALHSI: Agent Loop Harness Self-Improvement Showcase          "
echo "================================================================="
echo "Starting interactive web dashboard on http://${HOST}:${PORT}"
echo "Press Ctrl+C to stop."
echo ""

python3 -m alhsi serve --host "${HOST}" --port "${PORT}"
