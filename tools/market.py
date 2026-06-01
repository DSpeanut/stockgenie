import os

import yfinance as yf
from langchain_core.tools import tool


@tool
def market_price_tool(ticker: str):
    """Fetch the latest market stock price for a ticker using yfinance."""
    try:
        ticker_info = yf.Ticker(ticker)
        latest_price = ticker_info.history(period="5d").reset_index()["Close"].values[-1]
    except Exception:
        latest_price = "Currently Service is not available and no data found for the given ticker."
    return f"price for {ticker} from the latest date is {latest_price}"


@tool
def get_trend_signals(ticker: str):
    """Fetch technical trend signals (MA50, MA200, RSI, MACD) for a ticker."""
    df = yf.download(ticker, period="1y")
    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    ema12 = df["Close"].ewm(span=12).mean()
    ema26 = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9).mean()
    return (
        f"Latest 5 days trend signals for {ticker}: "
        f"{df[['Close', 'MA50', 'MA200', 'RSI', 'MACD', 'Signal']].tail(5).to_dict(orient='records')}"
    )
