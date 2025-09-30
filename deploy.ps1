# PowerShell deployment script for Windows
# Cross-platform replacement for deploy.sh

Write-Host "🌀 Starting Spiral Codex deployment..." -ForegroundColor Cyan

# Clean environment
Write-Host "🧹 Cleaning environment..." -ForegroundColor Yellow
if (Test-Path ".venv") { Remove-Item -Recurse -Force ".venv" }
if (Test-Path "codex_root") { Remove-Item -Recurse -Force "codex_root" }

# Create isolated environment
Write-Host "🐍 Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv .venv

# Activate virtual environment (Windows)
Write-Host "⚡ Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Upgrade pip and install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel
python -m pip install --prefer-binary -r requirements.txt

# Create structure
Write-Host "📁 Creating directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "codex_root\kernel"
New-Item -ItemType Directory -Force -Path "codex_root\agents"
New-Item -ItemType Directory -Force -Path "codex_root\config"

# Copy files (Windows-compatible paths)
Write-Host "📋 Copying files..." -ForegroundColor Yellow
if (Test-Path "kernel") { Copy-Item -Recurse "kernel\*" "codex_root\kernel\" }
if (Test-Path "agents") { Copy-Item -Recurse "agents\*" "codex_root\agents\" }
if (Test-Path "config") { Copy-Item -Recurse "config\*" "codex_root\config\" }

# Create entropy bindings config if it doesn't exist
$entropyConfig = @"
default_entropy: 0.5
thresholds:
  low: 0.3
  high: 0.9
"@

if (-not (Test-Path "codex_root\config\entropy_bindings.yml")) {
    Write-Host "⚙️ Creating entropy bindings config..." -ForegroundColor Yellow
    $entropyConfig | Out-File -FilePath "codex_root\config\entropy_bindings.yml" -Encoding UTF8
}

# Start API
Write-Host "🎛️ Launching FastAPI app on http://localhost:8000 ..." -ForegroundColor Green
Write-Host "Use Ctrl+C to stop the server" -ForegroundColor Yellow

# Use the correct FastAPI entrypoint
if (Test-Path "api\fastapi_app.py") {
    uvicorn api.fastapi_app:app --reload --host 127.0.0.1 --port 8000
} else {
    uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000
}
