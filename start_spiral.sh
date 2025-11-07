#!/bin/bash
# Spiral Codex startup script

# Change to the correct directory
cd /home/zebadiee/Documents/spiral_codex_unified

# Set environment variables
export SPIRAL_DIR="/home/zebadiee/Documents/spiral_codex_unified"
export PYTHONPATH="/home/zebadiee/Documents/spiral_codex_unified"
export PYTHONUNBUFFERED=1

# Start the FastAPI app
exec /home/zebadiee/Documents/spiral_codex_unified/.venv/bin/python fastapi_app.py