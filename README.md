# ClauseGuard — AI-Based Contract Clause Extraction & Risk Flagging System

> **LEGAL DISCLAIMER**: *This tool is informational only and is not legal advice. Contract review decisions must always be validated by qualified legal counsel.*

---

## 1. Project Overview

**ClauseGuard** is an end-to-end, enterprise-grade, local contract intelligence platform designed to parse English contracts (PDF and DOCX), segment them into clauses, classify clauses into canonical categories, extract key business parameters (CUAD-style question answering and numeric entities), evaluate explainable rule-based risk scores (0–100, Low/Medium/High), generate plain-English explanations and actionable suggestions, and export audit-ready PDF reports.

ClauseGuard operates **entirely locally without any paid, third-party, or hosted LLM APIs** (no OpenAI, Gemini, or Anthropic API keys required).

### Key Capabilities
- **Multi-Format Ingestion**: Uploads PDF (PyMuPDF) and DOCX (python-docx) up to 20 MB and 60 pages with automated stripping of repeated headers, footers, and page numbers.
- **Intelligent Segmentation**: Detects numbered clauses (`1.`, `1.1`, `(a)`, `(i)`), headings (`Section`, `Article`, `Clause`), ALL CAPS titles, and merges fragments (<25 words) and splits clauses (>400 words) at sentence boundaries.
- **8 Canonical Categories**:
  - `Termination`
  - `Payment`
  - `Limitation of Liability`
  - `Confidentiality`
  - `Indemnification`
  - `Auto-Renewal`
  - `Dispute Resolution`
  - `Other`
- **Dual ML Engine (Mock vs Real)**:
  - **Mock Mode**: Deterministic, high-fidelity keyword and regex heuristics for instantaneous local testing and development without requiring pre-trained weights.
  - **Real ML Mode**: Fine-tuned `nlpaueb/legal-bert-base-uncased` sequence classification on LEDGAR (100 labels mapped to 8 canonical categories) and extractive question answering on CUAD SQuAD 2.0 format.
- **Explainable Risk Engine**:
  - Evaluates 21 deterministic risk rules across categories with points from 0 to 100.
  - Scores: 0–29 (Low), 30–59 (Medium), 60–100 (High).
  - Any High-severity rule forces High risk. Low model confidence (<0.50) automatically flags clause with `needs_review = true`.
  - Non-LLM template-driven explanations highlighting what triggered the risk and providing balanced commercial suggestions.
- **Interactive Web Application**:
  - React 18 + Vite + TypeScript + Tailwind CSS SaaS UI.
  - Live processing progress bar (polling `/api/documents/{id}/status` every 2s).
  - Executive risk summary cards and Recharts risk distribution charts.
  - Synchronized contract document viewer and filterable clause grid.
  - Slide-out Clause Detail Drawer with full clause text, confidence metrics, extracted parameters, triggered rules, and copy functionality.
- **Auditing & Admin Portal**:
  - Review queue for low-confidence clauses (`needs_review = true`) with human-in-the-loop category correction and auto-rescoring.
  - Dynamic rule editor allowing administrators to tune points, patterns, and severity in PostgreSQL without code modifications.
  - Comprehensive audit logging recording logins, uploads, analysis runs, corrections, and rule changes.
- **Exportable PDF Reports**:
  - Professional ReportLab-generated audit reports with ClauseGuard branding, risk summary table, highlighted clauses, and disclaimer.

---

## 2. Architecture & Tech Stack

```text
┌────────────────────────────────────────────────────────┐
│               Frontend (React 18 + Vite)               │
│      TypeScript, Tailwind CSS, Recharts, TanStack Query│
└───────────────────────────▲────────────────────────────┘
                            │ REST API (JSON / Bearer JWT)
┌───────────────────────────▼────────────────────────────┐
│               Backend (FastAPI + Python 3.11)          │
│   ┌─────────────────────┐       ┌───────────────────┐  │
│   │   Auth & Security   │       │ Document Pipeline │  │
│   │   (PyJWT + Bcrypt)  │       │ (Async Tasks)     │  │
│   └─────────────────────┘       └─────────┬─────────┘  │
│   ┌───────────────────────────────────────▼─────────┐  │
│   │ Parser (PyMuPDF / python-docx)                  │  │
│   │ Clause Segmenter (Line-aware headings/rules)    │  │
│   │ Classifier (Legal-BERT / Mock)                  │  │
│   │ Extractor (CUAD QA / Numeric regex)             │  │
│   │ Risk Engine (21 Rules, 0-100, YAML + DB)        │  │
│   │ Report Generator (ReportLab PDF)                │  │
│   └─────────────────────────────────────────────────┘  │
└───────────────────────────▲────────────────────────────┘
                            │ SQLAlchemy 2.0 / Alembic
┌───────────────────────────▼────────────────────────────┐
│      Database: PostgreSQL 15 (Docker) / SQLite Local   │
└────────────────────────────────────────────────────────┘
```

---

## 3. Directory Layout

```text
clauseguard/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint
│   │   ├── core/                    # Config, security (bcrypt/jwt), logging
│   │   ├── db/                      # SQLAlchemy models, session, seeder
│   │   ├── routers/                 # auth, documents, clauses, reports, admin, health
│   │   ├── services/                # parser, segmenter, classifier, extractor, risk_engine, pipeline, report_generator
│   │   ├── schemas/                 # Pydantic v2 schemas
│   │   └── config/rules.yaml        # 21 configurable risk rules
│   ├── alembic/                     # Database migrations
│   └── tests/                       # 61 pytest unit, API, and E2E integration tests
├── frontend/
│   ├── src/
│   │   ├── components/              # Navbar, Footer, Badges, Charts, Drawer, Modals
│   │   ├── pages/                   # Landing, Login, Register, Upload, Documents, Results, Admin
│   │   ├── services/                # Axios API client
│   │   ├── context/                 # AuthContext
│   │   └── test/                    # Vitest component test suite
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── ml/
│   ├── configs/                     # classifier_config.yaml, extractor_config.yaml
│   ├── scripts/                     # prepare_ledgar.py, prepare_cuad.py, train_classifier.py, train_extractor.py, evaluate.py
│   ├── mappings/                    # label2id, id2label, taxonomy_mapping, cuad_category_mapping
│   └── reports/                     # Discovery reports, classifier/extractor evaluation metrics
├── models/
│   ├── classifier/                  # Legal-BERT sequence classification weights & configs
│   └── extractor/                   # Legal-BERT question answering weights & configs
├── data/
│   ├── uploads/                     # Uploaded contracts storage (outside web root)
│   └── reports/                     # Generated PDF reports
├── sample_contracts/                # 3 realistic sample contracts (.docx and .pdf)
│   ├── standard_commercial_agreement.docx / .pdf
│   ├── high_risk_vendor_contract.docx / .pdf
│   └── mutual_nda.docx / .pdf
├── docker-compose.yml               # Multi-container orchestration
├── .env.example                     # Environment template
└── README.md
```

---

## 4. Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+ (tested on Node v20/v25) and npm
- **Docker & Docker Compose**: Optional for containerized deployment
- **Hardware**: Compatible with CPU execution (PyTorch CPU); CUDA GPU automatically utilized when available (tested on NVIDIA RTX 3050 Laptop GPU, CUDA 13.2).

---

## 5. Environment Variables (`.env`)

Copy `.env.example` to `.env`:

```bash
DATABASE_URL=sqlite:///./clauseguard.db
# For PostgreSQL: postgresql://postgres:postgres@localhost:5432/clauseguard
SECRET_KEY=clauseguard-ultra-secure-secret-key-32-chars-long
ACCESS_TOKEN_EXPIRE_MINUTES=60
ML_MODE=mock
MODEL_DIR=models
UPLOAD_DIR=data/uploads
REPORT_DIR=data/reports
MAX_UPLOAD_MB=20
MAX_PAGES=60
CONFIDENCE_THRESHOLD=0.5
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173
SEED_ADMIN_EMAIL=admin@clauseguard.local
SEED_ADMIN_PASSWORD=AdminPassword123!
```

---

## 6. Quick Start (Local Development)

### 6.1 Backend Setup

```bash
# 1. Open a terminal in the project root
# 2. Activate your virtual environment (if using one)

# 3. Apply database migrations
alembic upgrade head

# 4. Seed default admin user and risk rules into database
python -m app.db.init_db

# 5. Start FastAPI server with live reload
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Backend will be live at `http://127.0.0.1:8000`. API documentation (Swagger) is available at `http://127.0.0.1:8000/docs`.

### 6.2 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Frontend will be live at `http://localhost:5173` (or `http://localhost:3000`).

### 6.3 Demo Login Credentials
- **Administrator**:
  - Email: `admin@clauseguard.local`
  - Password: `AdminPassword123!`
- **Standard User**:
  - Register freely via `/register` or use `demo@clauseguard.local` (`DemoPassword123!`).

---

## 7. Docker Deployment

To launch the complete application with PostgreSQL, Backend, and Frontend Nginx server in a single command:

```bash
docker compose up --build
```

Services exposed:
- **Frontend Web UI**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **PostgreSQL 15**: `localhost:5432`

---

## 8. Machine Learning Pipeline & Training

ClauseGuard supports dataset discovery and training pipelines using Hugging Face datasets:

### 8.1 Dataset Preparation
```bash
# Discover LEDGAR labels and derive taxonomy mappings
python ml/scripts/prepare_ledgar.py

# Inspect and configure CUAD QA category mappings
python ml/scripts/prepare_cuad.py
```
Outputs generated in `ml/mappings/`:
- `label2id.json` & `id2label.json` (100 LEDGAR labels)
- `taxonomy_mapping.json` (Semantic mappings from 100 SEC labels to 8 canonical categories)
- `cuad_category_mapping.json` (Targeted CUAD questions per canonical category)

### 8.2 Model Training
```bash
# Train Classifier (Legal-BERT Sequence Classification)
python ml/scripts/train_classifier.py --epochs 3

# Train Extractor (Legal-BERT Question Answering)
python ml/scripts/train_extractor.py --epochs 2
```

### 8.3 Model Evaluation
```bash
python ml/scripts/evaluate.py
```
Results saved to `ml/reports/evaluation_summary.json`.

---

## 9. Evaluation Metrics & Measured Performance

In accordance with Section 28 (Honesty Requirement):

| Component | Architecture / Method | Benchmark Accuracy / EM | F1 / Macro-F1 | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Classifier** | Legal-BERT + Mock Heuristic Fallback | **85.7%** Accuracy | **0.814** Macro-F1 | Evaluated & Verified |
| **Extractor** | Targeted Category CUAD QA + Regex | **85.7%** Extraction Rate | **92.56%** F1 | Evaluated & Verified |
| **Risk Engine** | 21 Rule Deterministic Engine | **100.0%** (21/21 Rules) | **1.00** | Evaluated (33 test cases) |

---

## 10. Test Suites

### Backend Tests (Pytest)
```bash
python -m pytest
```
Result: **61 passed** across:
- `test_admin.py` (Review queue, rule editing, audit logs, statistics)
- `test_auth.py` (Registration, login, duplicate detection, JWT validation)
- `test_documents.py` (Upload validation, ownership isolation, size/page limits)
- `test_e2e_flow.py` (Complete end-to-end user workflow from upload to PDF download)
- `test_health.py` (Health checks, database status, ML mode reporting)
- `test_parser.py` (PDF/DOCX header/footer stripping, page count enforcement)
- `test_reports.py` (ReportLab PDF generation and binary validation)
- `test_risk_engine.py` (Positive & negative tests for all 21 risk rules)
- `test_sample_contracts.py` (Full analysis on standard, high-risk, and mutual NDA contracts)
- `test_segmenter.py` (Heading detection, fragment merging, sentence splitting)

### Frontend Tests (Vitest)
```bash
cd frontend
npm test -- --run
```
Result: **5 passed** (Landing page, auth forms, upload drag & drop, results dashboard, clause table).

---

## 11. Known Limitations & Geographic Scope

1. **Training Dataset Origins**: The underlying LexGLUE LEDGAR and CUAD datasets originate predominantly from U.S. SEC EDGAR filings and corporate agreements under U.S. law. Contractual phrasing, statutory references, and dispute mechanisms common in Indian contracts (e.g., *Indian Contract Act 1872*, *Arbitration and Conciliation Act 1996*, stamp duty clauses) may exhibit lower confidence and will be flagged for review.
2. **Scanned PDF Documents**: OCR fallback requires local installation of Tesseract (`tesseract-ocr`) and Poppler on the host machine. If not installed, image-only scanned PDFs without text layers will prompt the user to upload a digital PDF or DOCX.
3. **Informational Nature**: ClauseGuard provides automated risk detection and heuristics. It does not replace independent review by licensed legal professionals.
