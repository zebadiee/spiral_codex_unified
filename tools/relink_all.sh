#!/usr/bin/env bash
set -euo pipefail

### ─────────────────────────────────────────────────────────────────────────────
### Relink All — Spiral ↔ OMAi ↔ Vault (with rollback)
### Declan-safe: idempotent, chatty, and won't nuke your setup.
### ─────────────────────────────────────────────────────────────────────────────

# Paths (edit if you've moved things)
SPIRAL_DIR="$HOME/Documents/spiral_codex_unified"
OMAI_DIR="$HOME/Documents/omarchy-ai-assist"
VAULT_DIR="${OMAI_VAULT_PATH:-$HOME/Documents/Obsidian/OMAi}"

# Environment source of truth
ENV_SRC="$OMAI_DIR/.env"                          # where your OR_* etc actually live
SPIRAL_ENV_LINK="$SPIRAL_DIR/.env"                # Spiral uses same env
SYSTEMD_ENV="$HOME/.config/systemd/user/spiral-codex.env"  # for systemd user services

# Systemd service names
SPIRAL_SVC="spiral-codex.service"
OMAI_SVC="omai-context.service"
VAULT_SYNC_TIMER="omai-vault-sync.timer"
REFLECT_TIMER="spiral-reflect.timer"

# Snapshot dir
STAMP="$(date +%F_%H%M%S)"
SNAP_DIR="$SPIRAL_DIR/archive/relink_safeguards/$STAMP"
mkdir -p "$SNAP_DIR"

info(){ echo -e "\033[1;36m[INFO]\033[0m $*"; }
ok(){   echo -e "\033[1;32m[OK]\033[0m   $*"; }
warn(){ echo -e "\033[1;33m[WARN]\033[0m $*"; }
err(){  echo -e "\033[1;31m[ERR]\033[0m  $*"; }

need() {
  command -v "$1" >/dev/null 2>&1 || { err "Missing dependency: $1"; exit 1; }
}

rollback() {
  warn "Rolling back from snapshot: $SNAP_DIR"
  # Put back any files we backed up
  for f in ".env" "configs/bridge.toml" "logs/wean.csv" "data/vault_index.json"; do
    if [ -f "$SNAP_DIR/$f" ]; then
      cp -f "$SNAP_DIR/$f" "$SPIRAL_DIR/$f" || true
    fi
  done
  # Try to restart services to pre-state
  systemctl --user daemon-reexec 2>/dev/null || true
  systemctl --user restart "$SPIRAL_SVC" "$OMAI_SVC" 2>/dev/null || true
  ok "Rollback attempted. Check services status."
  exit 1
}

trap 'err "Something failed. See logs above."; echo "Snapshot: $SNAP_DIR"; exit 1' INT TERM

### ─────────────────────────────────────────────────────────────────────────────
### Pre-flight
### ─────────────────────────────────────────────────────────────────────────────
need curl

[ -d "$SPIRAL_DIR" ] || { err "Missing $SPIRAL_DIR"; exit 1; }
[ -d "$OMAI_DIR" ]   || { err "Missing $OMAI_DIR"; exit 1; }

if [ ! -f "$ENV_SRC" ]; then
  warn "Expected env at $ENV_SRC - creating minimal version"
  cat > "$ENV_SRC" <<'ENV'
# OMAi + Spiral Unified Environment
OMAI_CONTEXT_PORT=7016
SPIRAL_API_PORT=8000
MCP_BRIDGE_PORT=7080
OMAI_VAULT_PATH=${HOME}/Documents/Obsidian/OMAi
ENV
fi

# Safety snapshot
info "Taking safety snapshot → $SNAP_DIR"
( cd "$SPIRAL_DIR"
  for f in ".env" "configs/bridge.toml" "logs/wean.csv" "data/vault_index.json"; do
    [ -f "$f" ] && install -D -m 0644 "$f" "$SNAP_DIR/$f"
  done
)
ok "Snapshot captured."

### ─────────────────────────────────────────────────────────────────────────────
### Phase 1 — Re-bind env for all components
### ─────────────────────────────────────────────────────────────────────────────
info "Re-linking environment to a single source of truth"
ln -sf "$ENV_SRC" "$SPIRAL_ENV_LINK"
mkdir -p "$(dirname "$SYSTEMD_ENV")"
ln -sf "$ENV_SRC" "$SYSTEMD_ENV"
ok "Env linked: Spiral + systemd now share $ENV_SRC"

### ─────────────────────────────────────────────────────────────────────────────
### Phase 2 — Bridge config (routes consolidated)
### ─────────────────────────────────────────────────────────────────────────────
BRIDGE_CFG="$SPIRAL_DIR/configs/bridge.toml"
mkdir -p "$(dirname "$BRIDGE_CFG")"
cat > "$BRIDGE_CFG" <<'TOML'
[routes]
chat    = "http://127.0.0.1:8000/v1/chat"
plan    = "http://127.0.0.1:8000/v1/brain/plan"
reflect = "http://127.0.0.1:8000/v1/reflect"
vault   = "http://127.0.0.1:7016"
TOML
ok "Bridge routes written ($BRIDGE_CFG)"

### ─────────────────────────────────────────────────────────────────────────────
### Phase 3 — Reload services under the unified env
### ─────────────────────────────────────────────────────────────────────────────
info "Reloading user services"
if command -v systemctl >/dev/null 2>&1; then
  systemctl --user daemon-reexec 2>/dev/null || warn "systemctl daemon-reexec not available"
  systemctl --user restart "$OMAI_SVC" "$SPIRAL_SVC" 2>/dev/null || warn "Services not found - manual start needed"
  sleep 2
  ok "Services restart attempted"
else
  warn "systemctl not available - services must be started manually"
fi

### ─────────────────────────────────────────────────────────────────────────────
### Phase 4 — Vault reindex setup
### ─────────────────────────────────────────────────────────────────────────────
info "Setting up vault reindex"
if curl -fsS -X POST "http://127.0.0.1:7016/api/context/reindex" >/dev/null 2>&1; then
  ok "Vault reindex endpoint responded."
else
  warn "Vault reindex endpoint not found; skipping trigger"
fi

# Create systemd units if systemctl available
if command -v systemctl >/dev/null 2>&1; then
  UNIT_DIR="$HOME/.config/systemd/user"
  mkdir -p "$UNIT_DIR"
  
  if [ ! -f "$UNIT_DIR/omai-vault-sync.service" ]; then
    cat > "$UNIT_DIR/omai-vault-sync.service" <<UNIT
[Unit]
Description=OMAi Vault Reindex

[Service]
Type=oneshot
ExecStart=/usr/bin/curl -fsS -X POST http://127.0.0.1:7016/api/context/reindex
UNIT
  fi

  if [ ! -f "$UNIT_DIR/omai-vault-sync.timer" ]; then
    cat > "$UNIT_DIR/omai-vault-sync.timer" <<UNIT
[Unit]
Description=Nightly OMAi Vault Reindex

[Timer]
OnCalendar=*-*-* 23:45:00
Persistent=true

[Install]
WantedBy=timers.target
UNIT
  fi

  systemctl --user daemon-reload 2>/dev/null || true
  systemctl --user enable --now "$VAULT_SYNC_TIMER" 2>/dev/null || warn "Timer setup requires manual systemctl"
  ok "Vault reindex timer configured"
fi

### ─────────────────────────────────────────────────────────────────────────────
### Phase 5 — Hourly reflection (self-correction)
### ─────────────────────────────────────────────────────────────────────────────
if command -v systemctl >/dev/null 2>&1; then
  UNIT_DIR="$HOME/.config/systemd/user"
  
  if [ ! -f "$UNIT_DIR/spiral-reflect.service" ]; then
    cat > "$UNIT_DIR/spiral-reflect.service" <<UNIT
[Unit]
Description=Spiral Reflection Cycle

[Service]
Type=oneshot
WorkingDirectory=$SPIRAL_DIR
ExecStart=/usr/bin/python3 $SPIRAL_DIR/reflection_training.py
UNIT
  fi

  if [ ! -f "$UNIT_DIR/$REFLECT_TIMER" ]; then
    cat > "$UNIT_DIR/$REFLECT_TIMER" <<UNIT
[Unit]
Description=Hourly Spiral Reflection

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
UNIT
  fi

  systemctl --user daemon-reload 2>/dev/null || true
  systemctl --user enable --now "$REFLECT_TIMER" 2>/dev/null || warn "Reflection timer requires manual systemctl"
  ok "Reflection timer configured"
fi

### ─────────────────────────────────────────────────────────────────────────────
### Verification — health + audit (if available)
### ─────────────────────────────────────────────────────────────────────────────
info "Verifying health…"
SPIRAL_OK="false"
OMAI_OK="false"

if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
  SPIRAL_OK="true"
fi

if curl -fsS http://127.0.0.1:7016/health >/dev/null 2>&1; then
  OMAI_OK="true"
fi

echo "Spiral OK: $SPIRAL_OK"
echo "OMAi   OK: $OMAI_OK"

if [[ "$SPIRAL_OK" != "true" && "$OMAI_OK" != "true" ]]; then
  warn "Both services appear down - you may need to start them manually"
  warn "Run: cd $SPIRAL_DIR && uvicorn fastapi_app:app --port 8000 &"
  warn "Run: cd $OMAI_DIR && node mcp_server.py &"
else
  ok "At least one service is healthy"
fi

# Legendary audit if present
if [ -x "$SPIRAL_DIR/legendary_system_audit.py" ]; then
  info "Running legendary audit…"
  ( cd "$SPIRAL_DIR" && ./legendary_system_audit.py ) || warn "Audit reported issues."
else
  warn "legendary_system_audit.py not found (skip)."
fi

### ─────────────────────────────────────────────────────────────────────────────
### Done
### ─────────────────────────────────────────────────────────────────────────────
ok "Relink complete. Snapshot stored at $SNAP_DIR"
echo
echo "Next steps:"
echo "  • curl http://localhost:8000/health"
echo "  • curl http://localhost:7016/health"
echo "  • tail -f $SPIRAL_DIR/logs/wean.csv (if exists)"
echo "  • Run: cd $SPIRAL_DIR && ./tools/spiral-pulse.sh"
