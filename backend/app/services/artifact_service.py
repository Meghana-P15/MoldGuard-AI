from __future__ import annotations

from pathlib import Path

import boto3

from backend.app.config import settings


MODEL_FILES = [
    "risk_model.joblib",
    "energy_model.joblib",
    "ood_model.joblib",
    "metadata.json",
    "risk_metrics.json",
    "energy_metrics.json",
    "training_summary.json",
]


class ArtifactService:
    @classmethod
    def ensure_local_models(cls) -> Path:
        model_dir = Path(settings.model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        if not settings.model_s3_bucket:
            return model_dir

        s3 = boto3.client("s3", region_name=settings.aws_region)
        prefix = settings.model_s3_prefix.strip("/")
        for filename in MODEL_FILES:
            target = model_dir / filename
            if target.exists() and not settings.refresh_models_from_s3:
                continue
            key = f"{prefix}/{filename}" if prefix else filename
            try:
                s3.download_file(settings.model_s3_bucket, key, str(target))
            except Exception:
                # Metrics are optional at serving time; model/core metadata are not.
                if filename in {"risk_metrics.json", "energy_metrics.json", "training_summary.json"}:
                    continue
                raise
        return model_dir
