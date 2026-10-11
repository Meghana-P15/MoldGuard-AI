from __future__ import annotations

import argparse
import json
import tarfile
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

ARTIFACT_FILES = [
    "risk_model.joblib",
    "energy_model.joblib",
    "ood_model.joblib",
    "metadata.json",
]


def package_model(model_dir: Path, out_path: Path) -> Path:
    missing = [name for name in ARTIFACT_FILES if not (model_dir / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing model artifacts: {missing}")

    with tarfile.open(out_path, "w:gz") as tar:
        for name in ARTIFACT_FILES:
            tar.add(model_dir / name, arcname=name)
    return out_path


def ensure_group(client, group_name: str) -> str:
    try:
        response = client.describe_model_package_group(ModelPackageGroupName=group_name)
        return response["ModelPackageGroupArn"]
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code not in {"ValidationException", "ResourceNotFound"}:
            raise

    response = client.create_model_package_group(
        ModelPackageGroupName=group_name,
        ModelPackageGroupDescription=(
            "Versioned MoldGuard risk + energy + OOD model bundle."
        ),
        Tags=[
            {"Key": "Project", "Value": "MoldGuard-AI"},
            {"Key": "Purpose", "Value": "Waste-Energy-Optimization"},
        ],
    )
    return response["ModelPackageGroupArn"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--image-uri", required=True, help="ECR URI for the custom SageMaker inference image")
    parser.add_argument("--region", default="ap-south-1")
    parser.add_argument("--group-name", default="MoldGuard-AI")
    parser.add_argument("--model-dir", default="ai/models")
    parser.add_argument("--approval", choices=["Approved", "Rejected", "PendingManualApproval"], default="PendingManualApproval")
    parser.add_argument("--prefix", default="registry")
    args = parser.parse_args()

    root = Path.cwd()
    model_dir = root / args.model_dir
    build_dir = root / ".moldguard_registry"
    build_dir.mkdir(exist_ok=True)

    tar_path = package_model(model_dir, build_dir / "model.tar.gz")

    metrics_path = model_dir / "training_metrics.json"
    if not metrics_path.exists():
        metrics_path = model_dir / "demo_metrics.json"
    if not metrics_path.exists():
        raise FileNotFoundError("No training_metrics.json or demo_metrics.json found.")

    s3 = boto3.client("s3", region_name=args.region)
    sm = boto3.client("sagemaker", region_name=args.region)

    model_key = f"{args.prefix.strip('/')}/model.tar.gz"
    metrics_key = f"{args.prefix.strip('/')}/metrics.json"
    s3.upload_file(str(tar_path), args.bucket, model_key)
    s3.upload_file(str(metrics_path), args.bucket, metrics_key)

    model_s3 = f"s3://{args.bucket}/{model_key}"
    metrics_s3 = f"s3://{args.bucket}/{metrics_key}"

    group_arn = ensure_group(sm, args.group_name)

    response = sm.create_model_package(
        ModelPackageGroupName=args.group_name,
        ModelPackageDescription=(
            "MoldGuard AI bundle: quality-risk classifier, energy regressor and OOD detector."
        ),
        ModelApprovalStatus=args.approval,
        Task="OTHER",
        InferenceSpecification={
            "Containers": [
                {
                    "Image": args.image_uri,
                    "ModelDataUrl": model_s3,
                    "Framework": "OTHER",
                }
            ],
            "SupportedContentTypes": ["application/json"],
            "SupportedResponseMIMETypes": ["application/json"],
            "SupportedRealtimeInferenceInstanceTypes": ["ml.m5.large"],
            "SupportedTransformInstanceTypes": ["ml.m5.large"],
        },
        ModelMetrics={
            "ModelQuality": {
                "Statistics": {
                    "ContentType": "application/json",
                    "S3Uri": metrics_s3,
                }
            }
        },
        MetadataProperties={
            "GeneratedBy": "MoldGuard SageMaker training pipeline",
        },
    )

    print(json.dumps({
        "model_package_group_arn": group_arn,
        "model_package_arn": response["ModelPackageArn"],
        "model_artifact": model_s3,
        "metrics": metrics_s3,
        "approval": args.approval,
    }, indent=2))


if __name__ == "__main__":
    main()
