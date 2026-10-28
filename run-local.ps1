# ClauseGuard -- Windows Local Development Startup Script (Without Docker)
# Run in PowerShell: .\run-local.ps1

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   ClauseGuard -- Local Development Launcher (No Docker)   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[1/6] Checking Python installation..." -ForegroundColor Yellow
$pyCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    $pyCmd = "py -3.11"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pyCmd = "python"
} else {
    Write-Error "Python 3.11 was not found on your system. Please install Python 3.11 and add it to PATH."
    exit 1
}
Write-Host "  -> Using Python: $pyCmd" -ForegroundColor Green

# 2. Check Node.js and npm
Write-Host "`n[2/6] Checking Node.js and npm..." -ForegroundColor Yellow
if (-not (Get-Command node -ErrorAction SilentlyContinue) -or -not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Error "Node.js and npm are required for the frontend. Please install Node.js."
    exit 1
}
$nodeVer = node --version
$npmVer = npm --version
Write-Host "  -> Node.js version: $nodeVer | npm version: $npmVer" -ForegroundColor Green

# 3. Create or verify backend virtual environment
Write-Host "`n[3/6] Verifying backend virtual environment..." -ForegroundColor Yellow
$venvPython = "$PSScriptRoot\backend\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "  -> Creating virtual environment at backend\.venv..." -ForegroundColor Cyan
    Invoke-Expression "$pyCmd -m venv --system-site-packages backend\.venv"
}

# Ensure pyvenv.cfg has include-system-site-packages = true
$cfgPath = "$PSScriptRoot\backend\.venv\pyvenv.cfg"
if (Test-Path $cfgPath) {
    $cfgContent = Get-Content $cfgPath -Raw
    if ($cfgContent -match "include-system-site-packages\s*=\s*false") {
        $cfgContent = $cfgContent -replace "include-system-site-packages\s*=\s*false", "include-system-site-packages = true"
        Set-Content -Path $cfgPath -Value $cfgContent
    }
}
Write-Host "  -> Virtual environment ready: backend\.venv" -ForegroundColor Green

# 4. Prepare directories and environment variables
Write-Host "`n[4/6] Ensuring required directories and environment variables..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "$PSScriptRoot\data\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "$PSScriptRoot\data\reports" | Out-Null
New-Item -ItemType Directory -Force -Path "$PSScriptRoot\models\classifier" | Out-Null
New-Item -ItemType Directory -Force -Path "$PSScriptRoot\models\extractor" | Out-Null

if (-not (Test-Path "$PSScriptRoot\.env")) {
    Copy-Item "$PSScriptRoot\.env.example" "$PSScriptRoot\.env"
    Write-Host "  -> Created .env from .env.example" -ForegroundColor Green
}
if (-not (Test-Path "$PSScriptRoot\backend\.env")) {
    Copy-Item "$PSScriptRoot\.env" "$PSScriptRoot\backend\.env"
}

# 5. Database migration & safe initialization
Write-Host "`n[5/6] Checking database and running safe migrations..." -ForegroundColor Yellow
Push-Location "$PSScriptRoot\backend"
try {
    & $venvPython -m alembic upgrade head
    & $venvPython -m app.db.init_db
} finally {
    Pop-Location
}
Write-Host "  -> Database migrated and verified (SQLite: clauseguard.db)" -ForegroundColor Green

# 6. Install frontend packages if missing
if (-not (Test-Path "$PSScriptRoot\frontend\node_modules")) {
    Write-Host "`n[6/6] Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location "$PSScriptRoot\frontend"
    try {
        npm install
    } finally {
        Pop-Location
    }
} else {
    Write-Host "`n[6/6] Frontend dependencies verified." -ForegroundColor Green
}

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "   ClauseGuard is configured and ready to run locally!    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Starting services in separate terminal windows..." -ForegroundColor Cyan

# Start Backend in a new window
$backendCmd = "cd '$PSScriptRoot\backend'; & '$venvPython' -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$backendCmd"
Write-Host "  [OK] Backend starting at:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "       API Documentation at: http://127.0.0.1:8000/docs" -ForegroundColor Gray
Write-Host "       Health Endpoint at:   http://127.0.0.1:8000/api/health" -ForegroundColor Gray

# Start Frontend in a new window
$frontendCmd = "cd '$PSScriptRoot\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$frontendCmd"
Write-Host "  [OK] Frontend starting at: http://localhost:5173" -ForegroundColor White

Write-Host "`nDemo Accounts:" -ForegroundColor Yellow
Write-Host "  Admin: admin@clauseguard.local / AdminSecurePass123!" -ForegroundColor White
Write-Host "  User:  Register any email at http://localhost:5173/register" -ForegroundColor White
Write-Host "`nDisclaimer: This tool is informational and is not legal advice." -ForegroundColor DarkYellow
