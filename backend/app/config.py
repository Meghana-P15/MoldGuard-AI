from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_dir: str = "ai/models"
    knowledge_dir: str = "knowledge/docs"
    use_dynamodb: bool = False
    dynamodb_table: str = "MoldGuardPredictions"
    aws_region: str = "ap-south-1"
    model_s3_bucket: str | None = None
    model_s3_prefix: str = "models/"
    refresh_models_from_s3: bool = False
    cors_origins: str = "http://localhost:5173"

    # Semantic RAG. `auto` tries Sentence Transformers + FAISS, then falls back
    # to TF-IDF if the embedding model is unavailable/offline.
    rag_backend: str = "auto"
    rag_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # App Runner stdout/stderr is collected by CloudWatch Logs. Optional custom
    # CloudWatch metrics can be enabled after AWS credentials/role are configured.
    enable_cloudwatch_metrics: bool = False
    cloudwatch_namespace: str = "MoldGuardAI"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
