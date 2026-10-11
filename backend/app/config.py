from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_dir: str = "ai/models"
    knowledge_dir: str = "knowledge"

    use_dynamodb: bool = False
    dynamodb_table: str = "MoldGuardPredictions"

    aws_region: str = "ap-south-1"
    model_s3_bucket: str | None = None
    model_s3_prefix: str = "models/"
    sync_models_from_s3: bool = False

    rag_embedder: str = "auto"
    rag_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Phase 4
    agent_mode: str = "local"  # local | agentcore
    agentcore_runtime_arn: str | None = None
    agentcore_qualifier: str = "DEFAULT"

    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
