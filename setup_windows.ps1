# Windows Setup Script for Spiral Codex Unified
# This script sets up the development environment on Windows 10/11

Write-Host "🌀 Setting up Spiral Codex Unified for Windows..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check Python version
$pythonVersionOutput = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$majorMinor = [float]$pythonVersionOutput
if ($majorMinor -lt 3.8) {
    Write-Host "❌ Python 3.8+ required. Found Python $pythonVersionOutput" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python version check passed" -ForegroundColor Green

# Create virtual environment
Write-Host "🐍 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Write-Host "⚠️ Removing existing .venv directory..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force ".venv"
}

python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "⚡ Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

# Upgrade pip and install dependencies
Write-Host "📦 Upgrading pip and installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install requirements" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️ requirements.txt not found, installing basic dependencies..." -ForegroundColor Yellow
    pip install fastapi uvicorn pydantic pytest
}

# Test imports
Write-Host "🧪 Testing imports..." -ForegroundColor Yellow
python -c "from api.fastapi_app import app; print('✅ FastAPI app imports successfully')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Import test failed" -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Yellow
pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Some tests failed, but continuing..." -ForegroundColor Yellow
} else {
    Write-Host "✅ All tests passed" -ForegroundColor Green
}

# Display next steps
Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate the virtual environment: .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Start the development server: uvicorn api.fastapi_app:app --reload --host 127.0.0.1 --port 8000" -ForegroundColor White
Write-Host "3. Or use the cross-platform deploy script: python deploy.py" -ForegroundColor White
Write-Host "4. Or use the PowerShell deploy script: .\deploy.ps1" -ForegroundColor White
Write-Host ""
Write-Host "The API will be available at: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "API documentation: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host ""
