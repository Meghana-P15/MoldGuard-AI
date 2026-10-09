# MoldGuard AI

**Prevent plastic scrap before production.**

MoldGuard AI predicts injection-molding batch viability, estimates cycle energy, explains the main risk drivers, and recommends nearby process settings that improve the probability of a good batch while reducing energy and avoiding unrealistic parameter jumps.

## Hackathon MVP

**Input → Risk prediction → Energy prediction → SHAP-style XGBoost contribution explanation → Optimization → Before/after impact**

### Team split
- **Meghana:** risk classifier, evaluation, explainability
- **Girish:** energy regressor, optimizer
- **Ragh:** FastAPI backend, AWS integration/deployment
- **Surya:** React frontend and UX

## Important dataset note

This repository ships with a **synthetic demo dataset only for smoke testing**. Do **not** present demo-model metrics as real-world performance.

For the final hackathon submission, retrain on the real injection-molding datasets listed in `docs/DATASETS.md`, validate the column mapping, and replace the artifacts in `ai/models/`.

## Quick start

### 1) Python environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

### 2) Generate demo data and train smoke-test models

```bash
python -m ai.training.generate_demo_data
python -m ai.training.train_all
```

### 3) Start backend from repository root

```bash
uvicorn backend.app.main:app --reload --port 8000
```

Open API docs: `http://localhost:8000/docs`

### 4) Start frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API

- `GET /health`
- `POST /api/predict`
- `POST /api/optimize`
- `GET /api/history`

See `docs/API_CONTRACT.md`.

## AWS path

Recommended:
- **S3:** datasets/model artifacts
- **SageMaker AI:** training/evaluation or managed inference
- **App Runner:** FastAPI
- **DynamoDB:** prediction history
- **CloudWatch:** logs/health
- **Amplify Hosting:** frontend

See `infrastructure/README.md`.

## Safety / scientific integrity

The optimizer is a software recommendation engine, not a machine-control system. It must stay within validated process bounds and should be reviewed by a qualified operator before real equipment use.
