# ClauseGuard — Windows Local Development Guide (No Docker)

> **LEGAL DISCLAIMER**: *This tool is informational and is not legal advice. Contract analysis decisions must always be validated by qualified legal professionals.*

---

## 1. Quick Start with One PowerShell Script

You can start the entire application (Backend + Frontend + SQLite database) with a single PowerShell script:

```powershell
# In PowerShell from project root:
.\run-local.ps1
```

This automated script will:
1. Verify Python 3.11 and Node.js are available.
2. Create or verify `backend\.venv`.
3. Ensure required directories (`data\uploads`, `data\reports`, `models`) and `.env` exist.
4. Run Alembic database migrations and seed the default admin account and 21 risk rules.
5. Launch the FastAPI backend on `http://127.0.0.1:8000` in a new PowerShell process.
6. Launch the Vite frontend on `http://localhost:5173` in a new PowerShell process.

---

## 2. Manual Startup Commands (Step-by-Step)

If you prefer starting services manually in separate terminals:

### Terminal 1: Backend (FastAPI + SQLite)

```powershell
# 1. Navigate to backend directory
cd "C:\Users\anupd\Desktop\Basic Claudeguard\backend"

# 2. Run database migrations and seeder
..\backend\.venv\Scripts\python.exe -m alembic upgrade head
..\backend\.venv\Scripts\python.exe -m app.db.init_db

# 3. Start Uvicorn development server
..\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Backend API**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/health`

### Terminal 2: Frontend (React 18 + Vite)

```powershell
# 1. Navigate to frontend directory
cd "C:\Users\anupd\Desktop\Basic Claudeguard\frontend"

# 2. Start Vite development server
npm run dev
```

- **Web Application**: `http://localhost:5173`

---

## 3. Local Configuration (`.env`)

The local environment is configured for SQLite and Mock ML mode:

```ini
DATABASE_URL=sqlite:///./clauseguard.db
SECRET_KEY=clauseguard_development_secret_key_at_least_32_chars_long_12345
ACCESS_TOKEN_EXPIRE_MINUTES=60
ML_MODE=mock
MODEL_DIR=./models
UPLOAD_DIR=./data/uploads
REPORT_DIR=./data/reports
MAX_UPLOAD_MB=20
MAX_PAGES=60
CONFIDENCE_THRESHOLD=0.5
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8000
SEED_ADMIN_EMAIL=admin@clauseguard.local
SEED_ADMIN_PASSWORD=AdminSecurePass123!
```

---

## 4. Test Credentials

- **Admin Account**:
  - Email: `admin@clauseguard.local`
  - Password: `AdminSecurePass123!`
  - Direct shortcut: Click **"Fill Admin Credentials"** on `http://localhost:5173/login`.
- **Standard User**:
  - Register freely via `http://localhost:5173/register` or create any demo user.

---

## 5. Sample Contracts for Testing

Pre-built realistic contracts are available in `sample_contracts/`:
1. `standard_commercial_agreement.docx` / `.pdf` — Standard, balanced contract.
2. `high_risk_vendor_contract.docx` / `.pdf` — High-risk contract triggering unilateral termination, unlimited customer liability, and broad indemnification.
3. `mutual_nda.docx` / `.pdf` — Clean, low-risk mutual NDA.

---

## 6. Running Automated Verification & Tests

### Run Full Live Workflow Verification
```powershell
.\backend\.venv\Scripts\python.exe verify_live_system.py
```
*Verifies registration, login, PDF/DOCX upload, asynchronous pipeline, risk engine, PDF report generation, ownership isolation, admin portal, and deletion.*

### Run Backend Pytest Suite (61 Tests)
```powershell
.\backend\.venv\Scripts\python.exe -m pytest
```

### Run Frontend Vitest Suite (5 Tests)
```powershell
cd frontend
npm test -- --run
```

---

## 7. How to Stop Services

- In each running PowerShell terminal, press `Ctrl + C`.
- Or terminate via PowerShell:
```powershell
Get-Process python, node -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*Basic Claudeguard*" } | Stop-Process
```
