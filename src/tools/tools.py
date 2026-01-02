import os
from langchain_core.tools import tool
import pandas as pd
import yaml
import requests
import yfinance as yf
from pathlib import Path
import chromadb
from config.config import PROMPTS_PATH, DATA_DIR, VECDB_PATH

with open(PROMPTS_PATH, "r") as f:
    data = yaml.safe_load(f)

@tool
def inventory_search_tool(ticker: str):
   """Search client investment inventory to find holding value and number of units information with ticker name"""
   holding_data = pd.read_csv(os.path.join(DATA_DIR, 'kis_holding_df.csv'))
   price = holding_data[holding_data['ticker']==ticker]['price'].values[0]
   units = holding_data[holding_data['ticker']==ticker]['qty'].values[0]
   profit = holding_data[holding_data['ticker']==ticker]['profit_rate'].values[0]
   return f"price: {price}, units: {units}, profit_rate: {profit}"

@tool
def market_price_tool(ticker: str):
    """fetch market price on last business day with a ticker"""
    ticker = yf.Ticker(ticker)  # Apple
    try:
        price = ticker.history(period="1d")["Close"]
    except:
        price = "Currently Service is not available and no data found for the given ticker."
    return price


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


