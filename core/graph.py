"""LangGraph construction and compilation."""

from langgraph.graph import END, StateGraph
from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter

from config.settings import settings
import os
from core.agent import Agent
from core.state import AgentState
from tools.finance import (
    calculate_per_pbr_score,
    fetch_employee_history,
    fetch_financial_metrics,
    search_company_general_info,
)
from tools.inventory import inventory_search_tool,portfolio_overview_tool
from tools.market import (
    currency_status_tool,
    get_trend_signals,
    market_price_tool,
    get_benchmark_tool,
)
from tools.news import news_search_tool


def build_agent() -> Agent:
    """Build and return the compiled StockGenie agent."""
    from langgraph.checkpoint.memory import MemorySaver

    # Select appropriate client based on configured API base.
    #if settings.openai_api_base and "openrouter" in settings.openai_api_base.lower():
    #router_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY") or settings.openai_api_key
    #model = ChatOpenRouter(api_key=router_key, base_url=settings.openai_api_base, model=settings.openai_model_name)
    #else:
    model = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-4o-mini")

    checkpointer = MemorySaver()

    tools = [
        market_price_tool,
        currency_status_tool,
        inventory_search_tool,
        get_benchmark_tool,
        portfolio_overview_tool,
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
