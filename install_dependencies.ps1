# PowerShell script to install dependencies
Write-Host "Installing dependencies for Data Analytics Agent..." -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    uv venv --python 3.12
    if ($LASTEXITCODE -ne 0) {
        uv venv --python 3.11
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing packages..." -ForegroundColor Yellow
uv pip install -r requirements.txt

# Also install google-genai if available
Write-Host "Installing google-genai (new API)..." -ForegroundColor Yellow
uv pip install google-genai 2>$null

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "To activate the virtual environment, run: .venv\Scripts\Activate.ps1" -ForegroundColor Cyan

