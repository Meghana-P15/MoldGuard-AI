from __future__ import annotations

from pathlib import Path
import boto3

from backend.app.config import settings


class ArtifactService:
    REQUIRED = [
        "risk_model.joblib",
        "energy_model.joblib",
        "metadata.json",
    ]
    OPTIONAL = [
        "ood_model.joblib",
        "demo_metrics.json",
    ]

    @classmethod
    def ensure_local_models(cls) -> Path:
        model_dir = Path(settings.model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)

        should_sync = bool(
            settings.model_s3_bucket
            and (
                settings.sync_models_from_s3
                or any(not (model_dir / name).exists() for name in cls.REQUIRED)
            )
        )

        if not should_sync:
            return model_dir

        s3 = boto3.client("s3", region_name=settings.aws_region)
        prefix = settings.model_s3_prefix.strip("/")

        for name in [*cls.REQUIRED, *cls.OPTIONAL]:
            key = f"{prefix}/{name}" if prefix else name
            target = model_dir / name
            try:
                s3.download_file(settings.model_s3_bucket, key, str(target))
            except Exception:
                if name in cls.REQUIRED and not target.exists():
                    raise

        return model_dir
