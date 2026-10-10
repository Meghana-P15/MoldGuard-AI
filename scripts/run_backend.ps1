Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path "ai\\models\\risk_model.joblib")) {
  python -m ai.training.train_all
}
uvicorn backend.app.main:app --reload --port 8000
