#!/bin/zsh

# Clean environment
rm -rf .venv codex_root

# Create isolated env
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --prefer-binary -r requirements.txt

# Create structure
mkdir -p codex_root/{kernel,agents,config}
cp -R kernel/* codex_root/kernel/
cp agents/* codex_root/agents/
cp config/* codex_root/config/

# Optional: simulate entropy bindings config
echo 'default_entropy: 0.5\nthresholds:\n  low: 0.3\n  high: 0.9' > codex_root/config/entropy_bindings.yml

# Start API (replace with uvicorn if needed)
echo "🎛️ Launching FastAPI app on http://localhost:8000 ..."
python3 api/fastapi_app.py
