# API Contract v2

Keep these canonical feature names unchanged across ML, backend and frontend:

```text
Tinj,tinj,Pinj,Ph,Bp,th
```

## POST `/api/analyze`

Recommended frontend endpoint. It returns prediction + uncertainty/guardrails +
optimization + grounded process evidence in one request.

Request:

```json
{
  "Tinj": 230,
  "tinj": 1.5,
  "Pinj": 32,
  "Ph": 18,
  "Bp": 22,
  "th": 6,
  "cycles": 10000,
  "part_weight_g": 18.5,
  "machine_id": "DEMO-01",
  "material_code": "PP"
}
```

Key response fields:

```json
{
  "run_id": "...",
  "prediction": {
    "prediction": "G",
    "decision": "LOW_RISK",
    "confidence": 0.82,
    "distribution": {
      "status": "IN_DISTRIBUTION"
    },
    "probabilities": {
      "G": 0.82,
      "Y": 0.12,
      "R": 0.06
    },
    "predicted_energy": 1.63,
    "energy_interval": {
      "low": 1.59,
      "high": 1.67
    },
    "material_impact": {}
  },
  "optimization": {
    "recommended_parameters": {},
    "improvement": {},
    "guardrail": {}
  },
  "evidence": [
    {
      "source": "demo_process_guidance.md",
      "section": "Injection pressure",
      "snippet": "...",
      "score": 0.42
    }
  ]
}
```

## Backward-compatible endpoints

- `POST /api/predict`
- `POST /api/optimize`
- `GET /api/history`
- `GET /api/knowledge?query=...`
- `GET /health`
