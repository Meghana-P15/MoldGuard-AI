# MoldGuard SageMaker Training + Model Registry

The repository now contains a complete deployable MLOps path:

```text
Real canonical CSV
  -> S3
  -> custom SageMaker training image
  -> risk + energy + OOD models
  -> optional Optuna tuning
  -> training_metrics.json
  -> SageMaker output model.tar.gz
  -> custom inference image in ECR
  -> SageMaker Model Registry
```

## A. Build/push the training image

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=ap-south-1
TRAIN_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/moldguard-training:latest

aws ecr create-repository --repository-name moldguard-training || true
aws ecr get-login-password --region $AWS_REGION \
  | docker login --username AWS --password-stdin \
    $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

docker build -f infrastructure/sagemaker/training/Dockerfile -t moldguard-training .
docker tag moldguard-training:latest $TRAIN_URI
docker push $TRAIN_URI
```

## B. Upload canonical real-data CSV to S3

The CSV must contain:

```text
Tinj,tinj,Pinj,Ph,Bp,th,label_viability,energy
```

Example:

```bash
aws s3 cp data/canonical_real.csv s3://YOUR_BUCKET/training/canonical_real.csv
```

## C. Launch SageMaker training

```bash
python scripts/launch_sagemaker_training.py \
  --role-arn YOUR_SAGEMAKER_ROLE_ARN \
  --image-uri $TRAIN_URI \
  --train-s3-uri s3://YOUR_BUCKET/training/ \
  --output-s3-uri s3://YOUR_BUCKET/sagemaker-output/ \
  --region $AWS_REGION \
  --optuna-trials 15
```

The SageMaker job writes a standard output `model.tar.gz` containing model artifacts and metrics.

## D. Build/push the inference image

See `MODEL_REGISTRY.md`. The custom inference image implements `/ping` and `/invocations` and can be associated with the registered model version.

## E. Register a versioned model

```bash
python scripts/register_sagemaker_model.py \
  --bucket YOUR_BUCKET \
  --image-uri YOUR_INFERENCE_ECR_URI \
  --region $AWS_REGION \
  --group-name MoldGuard-AI \
  --approval PendingManualApproval
```

Then open SageMaker Studio:

**Models -> Registered models -> MoldGuard-AI**
