# SageMaker Model Registry — MoldGuard

This repository now contains a real Model Registry path rather than only a diagram label.

## 1. Build the inference image

```bash
aws ecr create-repository --repository-name moldguard-inference

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=ap-south-1
ECR_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/moldguard-inference:latest

aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

docker build \
  -t moldguard-inference \
  infrastructure/sagemaker/inference

docker tag moldguard-inference:latest $ECR_URI
docker push $ECR_URI
```

PowerShell users can run the equivalent commands with environment variables.

## 2. Register the trained model bundle

```bash
python scripts/register_sagemaker_model.py \
  --bucket YOUR_MOLDGUARD_BUCKET \
  --image-uri $ECR_URI \
  --region ap-south-1 \
  --group-name MoldGuard-AI \
  --approval PendingManualApproval
```

This creates/uses a SageMaker Model Package Group and registers a versioned model bundle containing:

- `risk_model.joblib`
- `energy_model.joblib`
- `ood_model.joblib`
- `metadata.json`
- model-quality metrics

## 3. Hackathon demo

In SageMaker Studio, show:

**Models → Registered models → MoldGuard-AI → model version**

This proves the Model Registry box in the architecture is genuinely implemented.
