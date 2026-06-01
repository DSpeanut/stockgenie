import pytest


def test_settings_load():
    from config.settings import settings

    assert isinstance(settings.openai_api_key, str)
