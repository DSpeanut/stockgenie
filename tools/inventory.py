import json

import certifi
import pandas as pd
from langchain_core.tools import tool
from urllib.request import urlopen

from config.settings import DATA_DIR, INVENTORY_PATH


@tool
def inventory_search_tool(ticker: str):
    """Search client investment portfolio and holding by ticker."""
    holding_data = pd.read_csv(INVENTORY_PATH)
    stock = holding_data[holding_data["ovrs_pdno"] == ticker]
    name = stock["ovrs_item_name"].values[0]
    units = stock["ovrs_cblc_qty"].values[0]
    average_price = stock["pchs_avg_pric"].values[0]
    now_price = stock["now_pric2"].values[0]
    performance = stock["evlu_pfls_rt"].values[0]
    current_evaluation = stock["ovrs_stck_evlu_amt"].values[0]
    return (
        f"stock: {stock}, stock name: {name}, purchased unites: {units}, "
        f"average price: {average_price}, current price: {now_price}, "
        f"performance: {performance}, current evaluation: {current_evaluation}"
    )

@tool
def portfolio_overview_tool():
    """Provide an overview of the client's investment portfolio: every holding with ticker,
    name, units, average purchase price, current price, performance %, and current evaluation."""
    holding_data = pd.read_csv(INVENTORY_PATH)
    columns = [
        "ovrs_pdno",
        "ovrs_item_name",
        "ovrs_cblc_qty",
        "pchs_avg_pric",
        "now_pric2",
        "evlu_pfls_rt",
        "ovrs_stck_evlu_amt",
        "tr_crcy_cd",
    ]
    rows = holding_data[columns].rename(
        columns={
            "ovrs_pdno": "ticker",
            "ovrs_item_name": "name",
            "ovrs_cblc_qty": "units",
            "pchs_avg_pric": "avg_purchase_price",
            "now_pric2": "current_price",
            "evlu_pfls_rt": "performance_pct",
            "ovrs_stck_evlu_amt": "current_evaluation",
            "tr_crcy_cd": "currency",
        }
    )
    total_evaluation = rows["current_evaluation"].sum()
    lines = [row.to_dict() for _, row in rows.iterrows()]
    return f"Total portfolio evaluation: {total_evaluation:.2f}\nHoldings: {lines}"