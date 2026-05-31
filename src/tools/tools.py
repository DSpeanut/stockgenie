import os
from langchain_core.tools import tool
import pandas as pd
import yaml
import requests
import yfinance as yf
from pathlib import Path
import chromadb
from config.config import PROMPTS_PATH, DATA_DIR, VECDB_PATH, ENV_PATH
from datetime import datetime, timedelta
import certifi
import json
from urllib.request import urlopen
from dotenv import load_dotenv

load_dotenv(ENV_PATH,override=True)
FMP_API_KEY = os.getenv("FMP_API_KEY")

with open(PROMPTS_PATH, "r") as f:
    data = yaml.safe_load(f)


def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)

@tool
def inventory_search_tool(ticker: str):
   """Search client investment inventory to find holding value and number of units information with ticker name"""
   holding_data = pd.read_csv(os.path.join(DATA_DIR, 'kis_holding_df.csv'))
   stock = holding_data[holding_data['ovrs_pdno']==ticker]
   name = stock['ovrs_item_name'].values[0]
   units = stock['ovrs_cblc_qty'].values[0]
   average_price = stock['pchs_avg_pric'].values[0]
   now_price =stock['pchs_avg_pric'].values[0]
   performance = stock['evlu_pfls_rt'].values[0]
   current_evaluation = stock['ovrs_stck_evlu_amt'].values[0]
   return f"stock: {stock}, stock name: {name}, purchased unites: {units}, average price: {average_price}, current price: {now_price}, \
   performance: {performance}, current evaluation: {current_evaluation}"

@tool
def market_price_tool(ticker: str):
    """fetch market stock price on last business day with a ticker"""
    try:
        ticker_info = yf.Ticker(ticker)
        latest_price = ticker_info.history(period='5d').reset_index()['Close'].values[-1]
    except:
        latest_price = "Currently Service is not available and no data found for the given ticker."
    return f"price for {ticker} from the latest date is {latest_price}"


@tool
def news_search_tool(company: str):
    """fetch public news related to the company"""
    chroma_client = chromadb.PersistentClient(path=VECDB_PATH)
    collection = chroma_client.get_or_create_collection(name="news_collection")

    results = collection.query(
        query_texts=[f"the most recent news about {company}"],
        n_results=5
    )
    print(results[0])
    return results["documents"][0] if results and results["documents"] else []


@tool
def calculate_per_pbr_score(ticker: str):
    """Search per and pbr for stock with ticker name"""
    per = 0
    pbr = 0

    # Calculate PER score
    if per >= 10: 
        per_score = 5
    elif 8 < per < 10:
        per_score = 10
    elif 5 < per <= 8:
        per_score = 15
    else:
        per_score = 20

    # Calculate PBR score
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
def get_trend_signals(ticker: str):
    """Search for technical trend signals such as moving average, RSI, MACD for a ticker"""
    df = yf.download(ticker, period="1y")
    # Moving averages
    df["MA50"]  = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()
    # RSI
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rs    = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    # MACD
    ema12      = df["Close"].ewm(span=12).mean()
    ema26      = df["Close"].ewm(span=26).mean()
    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9).mean()
    return f"Latest 5 days trend signals for {ticker}: {df[['Close','MA50','MA200','RSI','MACD','Signal']].tail(5).to_dict(orient='records')}"

@tool
def fetch_financial_metrics(ticker: str):
    """Search for financial metrics such as P/E, P/B, PEG, ROE, net profit margin, Ebitda margin, debt-to-equity, current ratio, EPS (trailing), and free cash flow for a ticker"""
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info or {}
    metrics = {
        "P/E Ratio":          info.get("trailingPE"),
        "Forward P/E":        info.get("forwardPE"),
        "P/B Ratio":          info.get("priceToBook"),
        "PEG Ratio":          info.get("pegRatio"),
        "ROE":                info.get("returnOnEquity"),
        "Net Profit Margin":  info.get("profitMargins"),
        "Ebitda Margin":      info.get("ebitdaMargins"),
        "Debt-to-Equity":     info.get("debtToEquity"),
        "Current Ratio":      info.get("currentRatio"),
        "EPS (trailing)":     info.get("trailingEps"),
        "Free Cash Flow":     info.get("freeCashflow"),
    }

    return f"Trailing P/E: {metrics['P/E Ratio']}, Forward P/E: {metrics['Forward P/E']}, Price-to-Book: {metrics['P/B Ratio']}, PEG Ratio: {metrics['PEG Ratio']}, ROE: {metrics['ROE']}, Net Profit Margin: {metrics['Net Profit Margin']}, Ebitda Margin: {metrics['Ebitda Margin']}, Debt-to-Equity: {metrics['Debt-to-Equity']}, Current Ratio: {metrics['Current Ratio']}, EPS (trailing): {metrics['EPS (trailing)']}, Free Cash Flow: {metrics['Free Cash Flow']}"

@tool
def search_company_general_info(ticker: str):
    """Search for company information with ticker name such as current price, market capital size, beta, last dividend, price range, change percentage from previous day, stock volume, description"""
    company_info_serach_url = (f"https://financialmodelingprep.com/stable/profile?symbol={ticker}&apikey={FMP_API_KEY}")
    result = get_jsonparsed_data(company_info_serach_url)[0]
    current_price = result['price']
    market_cap = result['marketCap']
    beta = result['beta']
    lastDividend = str(result['lastDividend'])+'$'
    price_range = result['range']
    change_percentage_price_previousday = result['changePercentage']
    stock_volume = result['volume']
    stock_description = result['description']
    return f"Current Price: {current_price}$, Market Cap: {market_cap}$, Beta: {beta}, Last Dividend: {lastDividend}, Price Range: {price_range}, Change Percentage from Previous Day: {change_percentage_price_previousday}%, Stock Volume: {stock_volume}, Description: {stock_description}"

@tool
def fetch_employee_history(ticker: str):
    """ search for historical employee count and recent 5 trends with ticker name"""
    employee_url = (f"https://financialmodelingprep.com/stable/historical-employee-count?symbol={ticker}&apikey={FMP_API_KEY}")
    response = urlopen(employee_url, cafile=certifi.where())
    data = json.loads(response.read().decode('utf-8'))
    sorted_data = sorted(data, key=lambda x: x['periodOfReport'], reverse=True)
    trend_list = []
    for i in range(5):
        current_val = sorted_data[i]['employeeCount']
        previous_val = sorted_data[i+1]['employeeCount']
        change = ((current_val - previous_val) / previous_val) * 100
        direction = "Increase" if change > 0 else "Decrease"
        trend_list.append(f"{sorted_data[i]['periodOfReport']}: {change:.2f}% {direction}")
    most_recent_employees = sorted_data[0]['employeeCount']
    return f"Most Recent Count: {most_recent_employees}, Latest 5 employee count trends: {trend_list}"

# Example: fetch one prompt by name
def get_prompt(name, **kwargs):
    for p in data["prompts"]:
        if p["name"] == name:
            return p["prompt"].format(**kwargs)
    raise ValueError(f"Prompt '{name}' not found.")


