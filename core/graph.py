"""LangGraph construction and compilation."""

from langgraph.graph import END, StateGraph

from config.settings import settings
from core.agent import Agent
from core.state import AgentState
from tools.finance import (
    calculate_per_pbr_score,
    fetch_employee_history,
    fetch_financial_metrics,
    search_company_general_info,
)
from tools.inventory import inventory_search_tool
from tools.market import get_trend_signals, market_price_tool
from tools.news import news_search_tool


def build_agent() -> Agent:
    """Build and return the compiled StockGenie agent."""
    from langchain_openai import ChatOpenAI
    from langgraph.checkpoint.memory import MemorySaver

    model = ChatOpenAI(api_key=settings.openai_api_key, model="gpt-4o")
    checkpointer = MemorySaver()

    tools = [
        market_price_tool,
        inventory_search_tool,
        news_search_tool,
        get_trend_signals,
        calculate_per_pbr_score,
        fetch_financial_metrics,
        search_company_general_info,
        fetch_employee_history,
    ]

    # Load system prompt
    from config.prompts import get_prompt

    system = get_prompt("STOCK_GENIE_SYSTEM_PROMPT")

    agent = Agent(model=model, tools=tools, checkpointer=checkpointer, system=system)
    return agent
