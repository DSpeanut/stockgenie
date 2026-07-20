"""LangGraph construction and compilation."""

from langchain_openai import ChatOpenAI
from langchain_openrouter import ChatOpenRouter

from config.settings import settings
import os
from core.agent import Agent, Orchestrator
from core.skills import SKILLS
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
from tools.web_search import get_web_search
from observatory.tracking import init_tracing
from observatory.prompts import load_system_prompt


def build_agent() -> Orchestrator:
    """Build and return the compiled StockGenie orchestrator: router + general loop + skill loops."""
    from langgraph.checkpoint.memory import MemorySaver

    init_tracing()

    # Select appropriate client based on configured API base.
    #if settings.openai_api_base and "openrouter" in settings.openai_api_base.lower():
    #router_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY") or settings.openai_api_key
    #model = ChatOpenRouter(api_key=router_key, base_url=settings.openai_api_base, model=settings.openai_model_name)
    #else:
    model = ChatOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), model="gpt-4o-mini")

    checkpointer = MemorySaver()

    general_tools = [
        market_price_tool,
        currency_status_tool,
        inventory_search_tool,
        get_benchmark_tool,
        portfolio_overview_tool,
        news_search_tool,
        get_web_search,
        get_trend_signals,
        calculate_per_pbr_score,
        fetch_financial_metrics,
        search_company_general_info,
        fetch_employee_history,
    ]

    system = load_system_prompt()
    general_agent = Agent(model=model, tools=general_tools, checkpointer=None, system=system)

    return Orchestrator(model=model, general_agent=general_agent, skills=SKILLS, checkpointer=checkpointer)
