from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_dir: str = "ai/models"
    use_dynamodb: bool = False
    dynamodb_table: str = "MoldGuardPredictions"
    aws_region: str = "ap-south-1"
    model_s3_bucket: str | None = None
    model_s3_prefix: str = "models/"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
