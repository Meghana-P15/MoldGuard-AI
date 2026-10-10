# Architecture

```text
Operator
  |
  v
React + Vite + TypeScript
  |
  v
FastAPI (AWS App Runner)
  |
  +---------------------+
  |                     |
  v                     v
Risk classifier     Energy regressor
(XGBoost)           (XGBoost)
  |                     |
  +----------+----------+
             |
             v
    XGBoost contributions
      + optimizer
             |
             v
     Before/after result
             |
      +------+------+
      |             |
      v             v
 DynamoDB        CloudWatch

Artifacts/data -> S3
Training/evaluation -> SageMaker AI
Frontend -> Amplify Hosting
```

## Design principle

The LLM is not used to predict process quality. Traditional ML makes predictions. The decision engine optimizes only within defined parameter bounds. Generative AI may optionally explain results in plain language after the core system works.
