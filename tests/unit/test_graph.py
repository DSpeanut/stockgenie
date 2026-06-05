import sys
from unittest.mock import MagicMock

from config.settings import settings


def test_build_agent_uses_base_url(monkeypatch):
    monkeypatch.setitem(sys.modules, "chromadb", MagicMock())
    MockChatOpenAI = MagicMock()
    monkeypatch.setattr("langchain_openai.ChatOpenAI", MockChatOpenAI)
    monkeypatch.setattr(settings, "openai_api_base", "https://openrouter.ai/v1")
    monkeypatch.setattr(settings, "openai_model_name", "gpt-4o-mini")

    from core.graph import build_agent

    build_agent()

    MockChatOpenAI.assert_called_once_with(
        api_key=settings.openai_api_key,
        model=settings.openai_model_name,
        base_url=settings.openai_api_base,
    )
