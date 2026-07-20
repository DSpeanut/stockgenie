import pandas as pd
import tools.market as market
import tools.web_search as web_search

import pytest


def test_prompt_loader():
    from observatory.prompts import load_system_prompt

    try:
        prompt = load_system_prompt()
    except Exception:
        pytest.skip("MLflow tracking server not reachable")
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

def test_get_web_search(monkeypatch):
    class FakeClient:
        def __init__(self, api_key):
            self.api_key = api_key

        def search(self, query, search_depth):
            return {"query": query, "depth": search_depth, "result": "asset management insight"}

    monkeypatch.setattr(web_search, "TavilyClient", FakeClient)
    monkeypatch.setattr(web_search, "settings", type("S", (), {"tavily_api_key": "fake-key"})())

    result = web_search.get_web_search("test stock")
    assert "asset management insight" in result
    assert "test stock" in result
