# API contract

## `GET /api/meta`
Returns real machine/profile options, feature labels, bounds, model metrics, risk thresholds and active RAG backend.

## `POST /api/analyze`

Example request:

```json
{
  "machine": "I-10",
  "material": "A-PROD",
  "Tinj": 250,
  "tinj": 29,
  "Pinj": 140,
  "Ph": 65,
  "Tmold": 80,
  "th": 9,
  "cycles": 1000,
  "part_weight_g": 250
}
```

Response includes predicted real defect rate, G/Y/R risk band, validation-MAE uncertainty, OOD familiarity, XGBoost contribution drivers, real-power/energy estimate, recommended settings, candidate statistics, energy/defect/material impact, RAG evidence and human-review note.

## Compatibility endpoints

`POST /api/predict`, `POST /api/optimize`, and `GET /api/history` are also available.
