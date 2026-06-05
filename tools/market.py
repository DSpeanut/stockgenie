import re
import yfinance as yf
from langchain_core.tools import tool



@tool
def currency_status_tool(currencies: str = "USD,EUR,JPY,KRW"):
    """Fetch the currency status between usd, eur, krw, jpy and history using yfinance."""
    symbols = [s.upper() for s in re.split(r"[;,\s]+", currencies or "") if s] or list(CURRENCY_TICKER_MAP)
    periods = {"1w": 5, "1m": 21, "3m": 63, "6m": 126}
    out = {"summary": [], "data": {}}
    CURRENCY_TICKER_MAP = {
    "EUR": "USDEUR=X",
    "JPY": "USDJPY=X",
    "KRW": "USDKRW=X",
    }

    for symbol in symbols:
        ticker = CURRENCY_TICKER_MAP.get(symbol, f"{symbol}USD=X")
        history = yf.Ticker(ticker).history(period="6mo")
        if history.empty or "Close" not in history:
            out["data"][symbol] = {"ticker": ticker, "error": "no data"}
            out["summary"].append(f"{symbol}: no data")
            continue

        closes = history["Close"].dropna()
        if closes.empty:
            out["data"][symbol] = {"ticker": ticker, "error": "no valid prices"}
            out["summary"].append(f"{symbol}: no valid prices")
            continue

        latest = float(closes.iloc[-1])
        changes = {
            k: None
            if (p := float(closes.iloc[max(0, len(closes) - d - 1)])) == 0
            else round((latest - p) / p * 100, 4)
            for k, d in periods.items()
        }
        out["data"][symbol] = {"ticker": ticker, "latest": latest, "change": changes}
        out["summary"].append(
            f"{symbol}: {latest:.4f} | "
            + " | ".join(
                f"{k} {'n/a' if v is None else f'{v:+.2f}%'}" for k, v in changes.items()
            )
        )

    out["summary"] = "\n".join(out["summary"])
    return out


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
