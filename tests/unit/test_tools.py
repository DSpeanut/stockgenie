import pandas as pd
import tools.market as market

import pytest


def test_prompt_loader():
    from config.prompts import get_prompt

    prompt = get_prompt("STOCK_GENIE_SYSTEM_PROMPT")
    assert "financial advisor" in prompt.lower()


def test_currency_status_tool(monkeypatch):
    class FakeTicker:
        def __init__(self, ticker):
            self.ticker = ticker

        def history(self, period="6mo"):
            dates = pd.date_range("2026-01-01", periods=30, freq="B")
            values = [100 + i for i in range(len(dates))]
            return pd.DataFrame({"Close": values}, index=dates)

    monkeypatch.setattr(market.yf, "Ticker", FakeTicker)

    result = market.currency_status_tool("USD,EUR")
    assert isinstance(result, dict)
    assert "summary" in result and "data" in result
    assert "USD" in result["data"]
    assert "EUR" in result["data"]
    assert result["data"]["USD"]["latest"] == 129.0
    assert result["data"]["USD"]["change"]["1w"] == pytest.approx(4.0)
