"""Configuration settings using Pydantic for env vars and paths."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directories
BASE_DIR: Path = Path(__file__).parent.parent
DATA_DIR: Path = BASE_DIR / "data"
VECDB_PATH: Path = BASE_DIR / "chroma_db"
ENV_PATH: Path = BASE_DIR / ".env"
INVENTORY_PATH: Path = DATA_DIR / "kis_holding_df.csv"

# Load .env if it exists
if ENV_PATH.exists():
    load_dotenv(ENV_PATH, override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_api_base: str | None = Field(default=None, alias="OPENAI_API_BASE")
    openai_model_name: str = Field(default="gpt-4o", alias="OPENAI_MODEL")
    fmp_api_key: str = Field(default="", alias="FMP_API_KEY")
    newsapi_key: str = Field(default="", alias="NEWSAPI_KEY")
    tavily_api_key: str = Field(default="", alias="TAVILY_API_KEY")
    debug: bool = Field(default=False, alias="DEBUG")
    mlflow_tracking_uri: str = Field(default="http://127.0.0.1:5001", alias="MLFLOW_TRACKING_URI")
    mlflow_experiment_name: str = Field(default="stockgenie", alias="MLFLOW_EXPERIMENT_NAME")


settings = Settings()
