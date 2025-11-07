#!/bin/bash
# Install Spiral CLI permanently
set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           🔧 INSTALLING SPIRAL CLI PERMANENTLY 🔧                    ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Install to ~/bin (user-local)
mkdir -p ~/bin
cp spiral_cli.py ~/bin/spiral
chmod +x ~/bin/spiral
echo "✓ Installed to ~/bin/spiral"

# 2. Ensure ~/bin is in PATH
if ! echo "$PATH" | grep -q "$HOME/bin"; then
    echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
    echo "✓ Added ~/bin to PATH in .bashrc"
else
    echo "✓ ~/bin already in PATH"
fi

# 3. Create alias
if ! grep -q "alias spiral=" ~/.bash_aliases 2>/dev/null; then
    echo 'alias spiral="~/bin/spiral"' >> ~/.bash_aliases
    echo "✓ Created 'spiral' alias"
else
    echo "✓ Alias already exists"
fi

# 4. Create desktop entry (optional - for GUI)
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/spiral-cli.desktop <<'DESKTOP'
[Desktop Entry]
Name=Spiral CLI
Comment=Omarchy Spiral Codex Interface
Exec=gnome-terminal -- bash -c "cd ~/Documents/spiral_codex_unified && ~/bin/spiral; exec bash"
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=System;ConsoleOnly;
DESKTOP
echo "✓ Created desktop launcher"

# 5. Update Makefile
if ! grep -q "^spiral:" Makefile 2>/dev/null; then
    cat >> Makefile <<'MAKE'

# Spiral CLI shortcuts
spiral:
	@./spiral_cli.py

cli:
	@./spiral_cli.py

chat:
	@./spiral_cli.py
MAKE
    echo "✓ Added 'make spiral' shortcut"
else
    echo "✓ Makefile shortcuts already exist"
fi

# 6. Create documentation
cat > CLI_USAGE.md <<'DOC'
# Spiral CLI - Official Interface

## Installation
Run once: `./install_spiral_cli.sh`

## Usage

### Start Spiral CLI
```bash
spiral           # From anywhere (if ~/bin in PATH)
make spiral      # From project directory
make cli         # Alternative
make chat        # Alternative
```

### Commands
- `:quit` or `:q` - Exit and save session
- `:clear` - Clear conversation history
- `:stats` - Show brain statistics  
- `:help` - Show help

### Architecture
```
You → Spiral CLI → Spiral API (8000) → Agents → OpenRouter/Local
                → OMAi Vault (7016) for context
```

### Session Management
- Conversations persist in `~/.spiral_session`
- Last 100 exchanges kept
- Session survives restarts

### Auto-Fallback
1. Tries OpenRouter (your configured key)
2. Falls back to local models if needed
3. No manual switching required

## Troubleshooting

### CLI won't start
```bash
cd ~/Documents/spiral_codex_unified
make run  # Start Spiral API first
```

### Check system status
```bash
curl http://localhost:8000/health
curl http://localhost:7016/health
```

### View logs
```bash
tail -f logs/wean.csv        # Provider usage
tail -f ledger/conversations/*.jsonl  # Conversations
```
DOC
echo "✓ Created CLI_USAGE.md"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║              ✅ INSTALLATION COMPLETE ✅                              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "To activate now: source ~/.bashrc"
echo ""
echo "Usage:"
echo "  spiral           - Start CLI from anywhere"
echo "  make spiral      - Start from project directory"
echo "  :help            - Show commands in CLI"
echo ""
echo "Documentation: CLI_USAGE.md"
