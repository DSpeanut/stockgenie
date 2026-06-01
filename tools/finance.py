import json

import certifi
import yfinance as yf
from langchain_core.tools import tool
from urllib.request import urlopen

from config.settings import settings

FMP_API_KEY = settings.fmp_api_key


def _get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)


@tool
def calculate_per_pbr_score(ticker: str):
    """Calculate a simple PER and PBR score for a stock ticker."""
    per = 0
    pbr = 0
    if per >= 10:
        per_score = 5
    elif 8 < per < 10:
        per_score = 10
    elif 5 < per <= 8:
        per_score = 15
    else:
        per_score = 20
    if pbr >= 1.0:
        pbr_score = 0
    elif 0.6 < pbr <= 1.0:
        pbr_score = 3
    elif 0.3 < pbr <= 0.6:
        pbr_score = 4
    else:
        pbr_score = 5
    return f"PER score: {per_score}, PBR score: {pbr_score}"


@tool
def fetch_financial_metrics(ticker: str):
    """Fetch financial metrics (P/E, P/B, ROE, etc.) for a stock ticker using yfinance."""
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info or {}
    metrics = {
        "P/E Ratio": info.get("trailingPE"),
        "Forward P/E": info.get("forwardPE"),
        "P/B Ratio": info.get("priceToBook"),
        "PEG Ratio": info.get("pegRatio"),
        "ROE": info.get("returnOnEquity"),
        "Net Profit Margin": info.get("profitMargins"),
        "Ebitda Margin": info.get("ebitdaMargins"),
        "Debt-to-Equity": info.get("debtToEquity"),
        "Current Ratio": info.get("currentRatio"),
        "EPS (trailing)": info.get("trailingEps"),
        "Free Cash Flow": info.get("freeCashflow"),
    }
    return (
        f"Trailing P/E: {metrics['P/E Ratio']}, Forward P/E: {metrics['Forward P/E']}, "
        f"Price-to-Book: {metrics['P/B Ratio']}, PEG Ratio: {metrics['PEG Ratio']}, "
        f"ROE: {metrics['ROE']}, Net Profit Margin: {metrics['Net Profit Margin']}, "
        f"Ebitda Margin: {metrics['Ebitda Margin']}, Debt-to-Equity: {metrics['Debt-to-Equity']}, "
        f"Current Ratio: {metrics['Current Ratio']}, EPS (trailing): {metrics['EPS (trailing)']}, "
        f"Free Cash Flow: {metrics['Free Cash Flow']}"
    )


@tool
def search_company_general_info(ticker: str):
    """Search for company general info (price, market cap, beta, etc.) via FMP API."""
    url = f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={FMP_API_KEY}"
    result = _get_jsonparsed_data(url)[0]
    current_price = result["price"]
    market_cap = result["marketCap"]
    beta = result["beta"]
    last_dividend = str(result["lastDividend"]) + "$"
    price_range = result["range"]
    change_pct = result["changePercentage"]
    stock_volume = result["volume"]
    stock_description = result["description"]
    return (
        f"Current Price: {current_price}$, Market Cap: {market_cap}$, Beta: {beta}, "
        f"Last Dividend: {last_dividend}, Price Range: {price_range}, "
        f"Change Percentage from Previous Day: {change_pct}%, Stock Volume: {stock_volume}, "
        f"Description: {stock_description}"
    )


@tool
def fetch_employee_history(ticker: str):
    """Fetch historical employee count and recent trends via FMP API."""
    url = f"https://financialmodelingprep.com/stable/historical-employee-count?symbol={ticker}&apikey={FMP_API_KEY}"
    response = urlopen(url, cafile=certifi.where())
    data = json.loads(response.read().decode("utf-8"))
    sorted_data = sorted(data, key=lambda x: x["periodOfReport"], reverse=True)
    trend_list = []
    for i in range(5):
        current_val = sorted_data[i]["employeeCount"]
        previous_val = sorted_data[i + 1]["employeeCount"]
        change = ((current_val - previous_val) / previous_val) * 100
        direction = "Increase" if change > 0 else "Decrease"
        trend_list.append(f"{sorted_data[i]['periodOfReport']}: {change:.2f}% {direction}")
    most_recent_employees = sorted_data[0]["employeeCount"]
    return f"Most Recent Count: {most_recent_employees}, Latest 5 employee count trends: {trend_list}"
