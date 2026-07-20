"""MLflow Prompt Registry: source of truth for StockGenie's system prompt."""

import mlflow

from config.settings import settings

SYSTEM_PROMPT_NAME = "stockgenie-system-prompt"


def _use_registry() -> None:
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)


def register_system_prompt(template: str, commit_message: str) -> int:
    """Register a new version of the system prompt. Returns the new version number."""
    _use_registry()
    prompt = mlflow.genai.register_prompt(
        name=SYSTEM_PROMPT_NAME,
        template=template,
        commit_message=commit_message,
    )
    return prompt.version


def load_system_prompt(version: int | None = None) -> str:
    """Load the system prompt template from the MLflow Prompt Registry. Defaults to the latest version."""
    _use_registry()
    prompt = mlflow.genai.load_prompt(SYSTEM_PROMPT_NAME, version=version)
    return prompt.template
