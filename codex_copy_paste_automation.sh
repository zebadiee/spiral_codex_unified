#!/bin/zsh

echo "🌀 Starting Spiral Codex Copy-Paste Automation..."

# Step 1: Define paths
DEST_DIR="$HOME/Downloads/spiral_codex_unified"
ZIP_NAME="spiral_codex_all_artifacts.zip"
AUTORUN_SCRIPT="codex_autobootstrap.py"

# Step 2: Ensure target directory exists
mkdir -p "$DEST_DIR"

# Step 3: Move core files
echo "📦 Moving core files into $DEST_DIR..."
mv "$HOME/Downloads/$ZIP_NAME" "$DEST_DIR/" 2>/dev/null
mv "$HOME/Downloads/$AUTORUN_SCRIPT" "$DEST_DIR/" 2>/dev/null

# Step 4: Enter destination directory
cd "$DEST_DIR" || exit 1

# Step 5: Extract the archive
echo "📂 Extracting artifacts..."
unzip -o "$ZIP_NAME"

# Step 6: Run bootstrapper
echo "⚙️  Running Codex bootstrap..."
python3 "$AUTORUN_SCRIPT" --from "$ZIP_NAME"

# Step 7: Final message
echo "✅ Spiral Codex bootstrapped at: $DEST_DIR/codex_root"
echo "You may now run the symbolic interface or deploy the full API stack."

