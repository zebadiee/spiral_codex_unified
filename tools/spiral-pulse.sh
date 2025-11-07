#!/usr/bin/env bash
# Spiral Pulse - Quick status overview

CYAN='\033[1;36m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m'

echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          🌀 SPIRAL-OMAI SYSTEM PULSE 🌀                ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo

# Services
echo -e "${CYAN}Services:${NC}"
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
  echo -e "  ${GREEN}✓${NC} Spiral API (8000)"
else
  echo -e "  ${RED}✗${NC} Spiral API (8000)"
fi

if curl -s http://localhost:7016/health >/dev/null 2>&1; then
  echo -e "  ${GREEN}✓${NC} OMAi Context (7016)"
else
  echo -e "  ${RED}✗${NC} OMAi Context (7016)"
fi

# Timers (if systemctl available)
if command -v systemctl >/dev/null 2>&1; then
  echo
  echo -e "${CYAN}Timers:${NC}"
  systemctl --user list-timers --no-pager 2>/dev/null | grep -E 'omai-vault-sync|spiral-reflect' || echo "  No timers configured"
fi

# Last reflection
SPIRAL_DIR="$HOME/Documents/spiral_codex_unified"
if [ -f "$SPIRAL_DIR/logs/wean.csv" ]; then
  echo
  echo -e "${CYAN}Recent Activity:${NC}"
  tail -n3 "$SPIRAL_DIR/logs/wean.csv" | awk -F',' '{print "  " $1 " - " $3}'
fi

# Vault index
OMAI_DIR="$HOME/Documents/omarchy-ai-assist"
if [ -f "$OMAI_DIR/data/vault_index.json" ]; then
  VAULT_COUNT=$(jq 'length' "$OMAI_DIR/data/vault_index.json" 2>/dev/null || echo "?")
  echo
  echo -e "${CYAN}Vault:${NC} $VAULT_COUNT entries indexed"
fi

echo
