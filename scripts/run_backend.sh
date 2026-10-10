#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
if [ ! -f "ai/models/risk_model.joblib" ]; then
  python -m ai.training.train_all
fi
uvicorn backend.app.main:app --reload --port 8000
