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
PROMPTS_DIR: Path = BASE_DIR / "config" / "prompts"
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
    fmp_api_key: str = Field(default="", alias="FMP_API_KEY")
    newsapi_key: str = Field(default="", alias="NEWSAPI_KEY")
    debug: bool = Field(default=False, alias="DEBUG")

    @property
    def prompts_path(self) -> Path:
        return PROMPTS_DIR / "stockgenie.yaml"


settings = Settings()
