# API Contract

All team members should freeze these internal parameter names:

- `Tinj` - injection/melt temperature
- `tinj` - injection time
- `Pinj` - injection pressure
- `Ph` - holding pressure
- `Bp` - back pressure
- `th` - holding time
- `cycles` - planned production cycles

## POST `/api/predict`

Request:

```json
{
  "Tinj": 230,
  "tinj": 1.5,
  "Pinj": 30,
  "Ph": 18,
  "Bp": 25,
  "th": 6,
  "cycles": 10000
}
```

Response:

```json
{
  "prediction": "G",
  "risk_level": "LOW",
  "probabilities": {"G": 0.82, "Y": 0.12, "R": 0.06},
  "predicted_energy": 1.63,
  "top_risk_factors": [
    {"feature": "Pinj", "impact": -0.14, "direction": "decreases"}
  ],
  "projected_energy": 16300.0,
  "model_mode": "demo"
}
```

## POST `/api/optimize`

Returns current vs recommended parameters, predicted good-batch probability, energy, and projected energy change.

## GET `/api/history`

Returns the latest saved predictions. Local mode uses in-memory history; AWS mode uses DynamoDB.
