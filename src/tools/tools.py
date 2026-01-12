import os
from langchain_core.tools import tool
import pandas as pd
import yaml
import requests
import yfinance as yf
from pathlib import Path
import chromadb
from config.config import PROMPTS_PATH, DATA_DIR, VECDB_PATH
from datetime import datetime, timedelta

with open(PROMPTS_PATH, "r") as f:
    data = yaml.safe_load(f)

@tool
def inventory_search_tool(ticker: str):
   """Search client investment inventory to find holding value and number of units information with ticker name"""
   holding_data = pd.read_csv(os.path.join(DATA_DIR, 'kis_holding_df.csv'))
   stock = holding_data[holding_data['ovrs_pdno']==ticker]
   name = stock['ovrs_name'].values[0]
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
''' 
@tool
def search_per_pbr_score(ticker: str):
   """Search per and pbr for stock with ticker name"""
   per = 0
   pbr = 0

   if per>=10: 
       per_score = 5
   elif 8<per<10:
       per_score = 10
    elif 5<per<=8:
       per_score = 15
    else :
       per_score = 20
    
    if pbr>=10: 
       pbr_score = 5
    elif 8<pbr<10:
        pbr_score = 10
    elif 5<pbr]<=8:
       pbr_score = 15
    else :
       pbr_score = 20

   return f"price: {holding_price}, units: {holding_units}"
'''

# Example: fetch one prompt by name
def get_prompt(name, **kwargs):
    for p in data["prompts"]:
        if p["name"] == name:
            return p["prompt"].format(**kwargs)
    raise ValueError(f"Prompt '{name}' not found.")


