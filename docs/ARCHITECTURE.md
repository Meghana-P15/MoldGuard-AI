# MoldGuard AI architecture — final real-data version

1. Operator enters machine, material/energy profile, melt temperature, cycle time, injection pressure, holding pressure, **mold temperature (`Tmold`)**, holding time, cycles and part weight.
2. React/Vite calls `POST /api/analyze`.
3. FastAPI/Pydantic validates types, required fields and real-data operating bounds.
4. Orchestrator runs defect prediction, OOD detection, energy estimation, optimization, RAG and impact calculation.
5. ML inference:
   - XGBoost **defect-rate regressor** from `modelo.xlsx`.
   - Explicit G/Y/R thresholds after regression.
   - Isolation Forest OOD on real molding settings.
   - XGBoost electrical-power regressor from `test_dataset.csv`.
6. Optimizer evaluates 1,800 local candidates, rejects OOD candidates, minimizes predicted defect rate, minimizes estimated energy and penalizes large setting changes.
7. RAG uses Sentence Transformers + FAISS when available; TF-IDF is only the offline fallback. Public technical references and approved plant SOP text can be indexed from `knowledge/docs`.
8. Impact calculation reports energy change, predicted defect-rate change and material-at-risk change.
9. Human review is mandatory; no direct machine-control output exists.
10. History uses DynamoDB when enabled, otherwise local memory.
11. App Runner logs structured JSON to CloudWatch Logs; optional custom CloudWatch metrics expose latency, errors, OOD and decision counts.
12. SageMaker-compatible training produces model artifacts that can be stored in S3 and loaded by the backend.

## Data separation

The molding and electrical datasets lack a reliable common cycle key, so they are trained independently and combined only at inference/orchestration level. The code does not fabricate a row-wise relationship.
