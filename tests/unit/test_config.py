import pytest


def test_settings_load():
    from config.settings import settings

    assert isinstance(settings.openai_api_key, str)
    assert settings.openai_api_base is None or isinstance(settings.openai_api_base, str)
    assert isinstance(settings.openai_model_name, str)
