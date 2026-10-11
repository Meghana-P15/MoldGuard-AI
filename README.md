# MoldGuard AI — final real-data architecture

This repository uses **only two real datasets**:

- `ai/data/modelo.xlsx` — measured injection-molding process + defect data
- `ai/data/test_dataset.csv` — measured electrical / production telemetry

No synthetic training dataset is generated or used.

## Final ML architecture

- **XGBoost defect-rate regressor** trained on real `%Defectuosos` from `modelo.xlsx`
- **Explicit risk thresholds** applied after prediction: GOOD ≤ 5%, WARNING >5% to ≤6%, HIGH RISK >6%
- **Isolation Forest OOD detector** trained on the same real process settings
- **XGBoost power regressor** trained directly on real `TOTAL_ACT_POWER` from `test_dataset.csv`
- **Tmold** is the measured mold-temperature input; no fake back-pressure feature is used
- **1,800-candidate constrained optimizer** minimizing defect rate, energy estimate and large setting changes
- **Sentence Transformers + FAISS semantic RAG** when available, with TF-IDF fallback for offline operation
- **Structured JSON logs + optional custom CloudWatch metrics**
- DynamoDB history, S3 model artifact loading, SageMaker training entrypoint, App Runner and Amplify configs

## Train

```bash
pip install -r requirements.txt
python -m ai.training.train_all
```

Artifacts:

```text
ai/models/risk_model.joblib      # XGBoost defect-rate regressor
ai/models/ood_model.joblib       # Isolation Forest
ai/models/energy_model.joblib    # XGBoost power regressor
ai/models/metadata.json
ai/models/risk_metrics.json
ai/models/energy_metrics.json
ai/models/training_summary.json
```

## Run backend

```bash
uvicorn backend.app.main:app --reload
```

Swagger: `http://localhost:8000/docs`

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

## Request flow

```text
Operator
  ↓
React Decision Cockpit
  ↓
FastAPI /api/analyze + Pydantic validation
  ↓
Prediction Orchestration
  ├─ XGBoost defect-rate regression → G/Y/R thresholds
  ├─ Isolation Forest OOD
  ├─ XGBoost real-power regression → kWh/cycle
  ├─ Constrained multi-objective optimizer
  ├─ Semantic RAG evidence
  └─ Impact calculation
  ↓
Interactive recommendation + mandatory human review
  ↓
DynamoDB history (when enabled)
```

## Real-data separation

The two datasets do not share a reliable cycle identifier, so they are **not** artificially joined row-by-row. Defect/OOD learning comes from `modelo.xlsx`; electrical power learning comes from `test_dataset.csv`. Their outputs are combined only in the application decision layer.

## RAG

`knowledge/docs/` contains public technical guidance plus the real-data operating envelope. Public guidance is **not represented as the factory's own SOP**. For deployment, place approved site SOP text/doc exports into `knowledge/docs/`; the semantic retriever will index them automatically.

`RAG_BACKEND=auto` tries `sentence-transformers/all-MiniLM-L6-v2` with FAISS. If embeddings cannot load (for example, an offline laptop without the model cached), it safely uses TF-IDF fallback and reports the active backend in `/health` and `/api/meta`.

## CloudWatch observability

App Runner captures stdout/stderr JSON logs in CloudWatch Logs. Set `ENABLE_CLOUDWATCH_METRICS=true` after attaching an IAM role with `cloudwatch:PutMetricData` to emit API latency, OOD count, review-required count, high-risk count and predicted-defect metrics.
