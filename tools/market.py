import re
import yfinance as yf
from langchain_core.tools import tool



@tool
def currency_status_tool(currencies: str = "USD,EUR,JPY,KRW"):
    """Simple currency status: latest price, 1-week and 1-month percent changes.

    Returns a dict: {summary, data} where data[currency] = {ticker, latest, 1w, 1m}.
    """
    symbols = [s.upper() for s in re.split(r"[;,\s]+", currencies or "") if s] or ["USD", "EUR", "JPY", "KRW"]
    M = {"USD": "^DXY", "EUR": "EURUSD=X", "JPY": "USDJPY=X", "KRW": "USDKRW=X"}
    out = {"summary": [], "data": {}}

    for symbol in symbols:
        ticker = M.get(symbol, f"{symbol}USD=X")
        try:
            hist = yf.Ticker(ticker).history(period="1mo")
            if hist.empty or "Close" not in hist:
                out["data"][symbol] = {"ticker": ticker, "error": "no data"}
                out["summary"].append(f"{symbol}: no data")
                continue

            closes = hist["Close"].dropna()
            if closes.empty:
                out["data"][symbol] = {"ticker": ticker, "error": "no valid prices"}
                out["summary"].append(f"{symbol}: no valid prices")
                continue

            latest = float(closes.iloc[-1])
            idx_1w = max(0, len(closes) - 5 - 1)
            idx_1m = 0
            prior_1w = float(closes.iloc[idx_1w])
            prior_1m = float(closes.iloc[idx_1m])

            def pct(a, b):
                return None if b == 0 else round((a - b) / b * 100, 2)

            out["data"][symbol] = {
                "ticker": ticker,
                "latest": latest,
                "1w": pct(latest, prior_1w),
                "1m": pct(latest, prior_1m),
            }
            out["summary"].append(f"{symbol}: {latest:.4f} | 1w {out['data'][symbol]['1w']}% | 1m {out['data'][symbol]['1m']}%")
        except Exception as e:
            out["data"][symbol] = {"ticker": ticker, "error": str(e)}
            out["summary"].append(f"{symbol}: error")

    out["summary"] = "; ".join(out["summary"])
    return out


@tool
def get_benchmark_tool(ticker: str, time_window: str ):
    """Fetch concise benchmarks for core US indices. Some benchmark examples are S&P 500, Nasdaq Composite, Dow Jones Industrial Average, Russell 2000.
    Use the corresponding tickers to fetch the information. For example, S&P 500 is ^GSPC, Nasdaq Composite is ^IXIC, Dow Jones Industrial Average is ^DJI, Russell 2000 is ^RUT.
    available period are 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd. choose the time window accordingly
    Returns oldest and latest closing price for the given time window.
    """
    history = yf.Ticker(ticker).history(period=time_window)
    open_benchmark = history["Open"].dropna().iloc[0] 
    closes_benchmark = history["Close"].dropna().iloc[-1]
    return f'Oldest closing price: {open_benchmark}, Latest closing price: {closes_benchmark}'

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
