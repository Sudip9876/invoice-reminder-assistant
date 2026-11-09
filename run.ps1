Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting Invoice & Payment-Reminder Assistant (Multi-Page)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found. Please run:" -ForegroundColor Red
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "Launching multi-page Streamlit dashboard..." -ForegroundColor Green
& ".venv\Scripts\streamlit.exe" run app.py
