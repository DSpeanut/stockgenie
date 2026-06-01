import pytest


def test_prompt_loader():
    from config.prompts import get_prompt

    prompt = get_prompt("STOCK_GENIE_SYSTEM_PROMPT")
    assert "financial advisor" in prompt.lower()
