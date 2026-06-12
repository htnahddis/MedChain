# MedChain Backend — Setup Guide

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.12+ | 3.14 works, avoid 3.11- |
| PostgreSQL | 16+ | 18 recommended |
| Git | any | to clone repo |

---

## Step 1 — Install PostgreSQL

### Windows
Download installer from https://www.postgresql.org/download/windows/  
During install:
- Set a password for the `postgres` superuser (remember it)
- Keep default port: `5432`

After install, add `psql` to PATH (run in PowerShell as **Administrator**):
```powershell
[System.Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";C:\Program Files\PostgreSQL\18\bin", "Machine")
```
Close and reopen terminal after this.

### Linux (Ubuntu/Debian)
```bash
sudo apt install postgresql postgresql-contrib -y
sudo systemctl start postgresql
```

### macOS
```bash
brew install postgresql@16
brew services start postgresql@16
```

---

## Step 2 — Create Database & User

Run in terminal (replace `YOUR_PASSWORD` with a password you choose):

### Windows (PowerShell as Administrator)
```powershell
net start postgresql-x64-18        # start service
psql -U postgres -c "CREATE USER medchain_user WITH PASSWORD 'YOUR_PASSWORD';"
psql -U postgres -c "CREATE DATABASE medchain_db OWNER medchain_user;"
```

### Linux / macOS
```bash
sudo -u postgres psql -c "CREATE USER medchain_user WITH PASSWORD 'YOUR_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE medchain_db OWNER medchain_user;"
```

---

## Step 3 — Clone & Configure

```bash
git clone <repo-url>
cd Project_Medchain/backend
```

Create `.env` file in the `backend/` folder:

```env
# Database — update password to match what you set above
DATABASE_URL=postgresql://medchain_user:YOUR_PASSWORD@localhost:5432/medchain_db

# Groq AI — get free key at https://console.groq.com/
GROQ_API_KEY=your_groq_api_key_here

# OpenFDA (optional)
OPENFDA_API_KEY=

# App settings
HOSPITAL_BED_COUNT=500
FORECAST_HORIZON_DAYS=90
SERVICE_LEVEL=0.95
DEBUG=true
SECRET_KEY=change-this-in-production

# CORS — set to your frontend URL
FRONTEND_URL=http://localhost:5173
```

> **Note:** If your password contains special characters (e.g. `@`), URL-encode them.  
> `@` → `%40`, `#` → `%23`, `$` → `%24`  
> Example: password `P@ss#1` → `DATABASE_URL=...medchain_user:P%40ss%231@localhost...`

---

## Step 4 — Install Dependencies

### Option A — uv (fast, recommended)
```bash
pip install uv
uv venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

uv pip install -r requirements.txt
```

### Option B — pip
```bash
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Step 5 — Seed the Database

Run **once** to populate 28 medicines + 365 days of synthetic data:

```bash
# Windows:
.\.venv\Scripts\python.exe -m app.utils.seed_data

# Linux/macOS:
.venv/bin/python -m app.utils.seed_data
```

Expected output:
```
Seeding suppliers...
Seeding medicines + consumption data...
  [OK] Amoxicillin 500mg - 365 consumption records
  [OK] ORS Sachets - 365 consumption records
  ...
[DONE] Seeding complete!
   28 medicines
   10 suppliers
   10220 consumption records
```

---

## Step 6 — Run the Server

```bash
# Windows:
.\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

# Linux/macOS:
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Server starts at → **http://localhost:8000**  
Swagger docs at  → **http://localhost:8000/docs**

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/` | Root health check |
| GET | `/health` | Health status |
| GET | `/api/medicines/` | List all 28 medicines |
| GET | `/api/medicines/{id}` | Get medicine by ID |
| POST | `/api/medicines/` | Add new medicine |
| GET | `/api/medicines/risk-scores/all` | Risk scores for all medicines |
| GET | `/api/forecast/stockout-risk/all?horizon=30` | Stockout probabilities (30/60/90 days) |
| GET | `/api/forecast/risk-scores/all` | Risk score table |
| GET | `/api/forecast/{medicine_id}?horizon_days=90` | Demand forecast for one medicine |
| GET | `/api/reorder/recommendations` | Reorder queue (URGENT/WARNING items) |
| POST | `/ai-insights/` | AI supply chain analysis (Groq Llama 70B) |

---

## Troubleshooting

### `psql: command not found`
PostgreSQL `bin/` not in PATH — add it (see Step 1).

### `connection refused` on port 5432
PostgreSQL service not running:
- Windows: `net start postgresql-x64-18` (as Admin)
- Linux: `sudo systemctl start postgresql`
- macOS: `brew services start postgresql@16`

### `ModuleNotFoundError: No module named 'app'`
Run commands from inside the `backend/` directory, not project root.

### `UnicodeEncodeError` on Windows terminal
Emoji in output — harmless, seed still completes. Use Windows Terminal instead of old cmd.

### AI endpoint returns `GROQ_API_KEY not configured`
Add your key to `.env`. Get free key at https://console.groq.com/

---

## Get a Groq API Key (Free)

1. Go to https://console.groq.com/
2. Sign up / log in
3. Keys → Create API Key
4. Paste into `.env` as `GROQ_API_KEY=gsk_...`

Model used: **llama-3.3-70b-versatile** (free tier, 30 req/min)
