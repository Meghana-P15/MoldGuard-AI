from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AgentConfig:
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    bedrock_model_id: str = os.getenv(
        "BEDROCK_MODEL_ID",
        "global.anthropic.claude-sonnet-4-5-20250929-v1:0",
    )
    model_dir: str = os.getenv("MODEL_DIR", str(ROOT / "ai" / "models"))
    knowledge_dir: str = os.getenv("KNOWLEDGE_DIR", str(ROOT / "knowledge"))
    model_s3_bucket: str | None = os.getenv("MODEL_S3_BUCKET")
    model_s3_prefix: str = os.getenv("MODEL_S3_PREFIX", "models/")
    sync_models_from_s3: bool = (
        os.getenv("SYNC_MODELS_FROM_S3", "false").lower() == "true"
    )
    rag_embedder: str = os.getenv("RAG_EMBEDDER", "tfidf")


settings = AgentConfig()
