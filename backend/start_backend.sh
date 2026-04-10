#!/usr/bin/env bash
# ─────────────────────────────────────────────
#  TNSchemesBot – Backend Startup Script
# ─────────────────────────────────────────────
# Run from project root:  bash backend/start_backend.sh
# Or make executable:     chmod +x backend/start_backend.sh && ./backend/start_backend.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$PROJECT_DIR/.venv"
BACKEND="$PROJECT_DIR/backend"

echo "📂 Project: $PROJECT_DIR"
echo "🐍 Using venv: $VENV"

# Activate venv
source "$VENV/bin/activate"

# Ensure static dirs/seed files exist
mkdir -p "$BACKEND/static/upload"
[ -f "$BACKEND/static/det.txt" ]    || echo "1" > "$BACKEND/static/det.txt"
[ -f "$BACKEND/static/scheme.txt" ] || echo "0" > "$BACKEND/static/scheme.txt"

echo ""
echo "✅ All checks passed. Starting Flask backend on http://localhost:3000 ..."
echo "   (Press Ctrl+C to stop)"
echo ""

# Run Flask from the backend directory so relative paths (static/) resolve correctly
cd "$BACKEND"
python main.py
