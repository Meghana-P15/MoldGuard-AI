from __future__ import annotations

from pathlib import Path
import boto3

from agentic.config import settings


REQUIRED = [
    "risk_model.joblib",
    "energy_model.joblib",
    "metadata.json",
]
OPTIONAL = [
    "ood_model.joblib",
    "demo_metrics.json",
]


def ensure_model_artifacts() -> Path:
    model_dir = Path(settings.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    missing = [name for name in REQUIRED if not (model_dir / name).exists()]
    should_sync = bool(
        settings.model_s3_bucket
        and (settings.sync_models_from_s3 or missing)
    )

    if not should_sync:
        return model_dir

    s3 = boto3.client("s3", region_name=settings.aws_region)
    prefix = settings.model_s3_prefix.strip("/")

    for name in [*REQUIRED, *OPTIONAL]:
        target = model_dir / name
        key = f"{prefix}/{name}" if prefix else name
        try:
            s3.download_file(settings.model_s3_bucket, key, str(target))
        except Exception:
            if name in REQUIRED and not target.exists():
                raise

    return model_dir
