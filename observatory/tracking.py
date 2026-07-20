"""MLflow tracing setup: points the app at the tracking server and traces every LLM call."""

import mlflow

from config.settings import settings

_initialized = False


def init_tracing() -> None:
    """Enable LangChain/LangGraph autologging to MLflow. Idempotent per process."""
    global _initialized
    if _initialized:
        return

    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)
    mlflow.langchain.autolog(log_traces=True)
    _initialized = True
