# Person-by-person build plan

## Meghana — risk ML + explainability
Tech: Python, pandas, NumPy, scikit-learn, XGBoost, SHAP/XGBoost contributions, Matplotlib, joblib.

Deliver:
- cleaned feature table
- classifier
- metrics + confusion matrix
- `predict_risk`
- top risk drivers

## Girish — energy + optimizer
Tech: Python, pandas, NumPy, scikit-learn, XGBoost, SciPy/random constrained search, joblib.

Deliver:
- energy model
- optimizer with process bounds
- before/after impact

## Ragh — backend + AWS
Tech: FastAPI, Pydantic, Uvicorn, boto3, S3, DynamoDB, App Runner, CloudWatch.

Deliver:
- `/health`
- `/api/predict`
- `/api/optimize`
- `/api/history`
- AWS deployment

## Surya — frontend
Tech: React, Vite, TypeScript, Recharts, CSS, Amplify Hosting.

Deliver:
- machine input card
- risk probabilities
- risk-driver chart
- optimized settings comparison
- energy impact
