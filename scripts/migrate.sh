#!/usr/bin/env bash
# Run inside the api container or locally with venv active
set -euo pipefail

echo "▶ Running Alembic migrations..."
cd /app
alembic upgrade head
echo "✓ Migrations complete"
