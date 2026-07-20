from langchain_core.tools import tool
from config.settings import settings

try:
    from tavily import TavilyClient
except ImportError:  # pragma: no cover
    TavilyClient = None


@tool
def get_web_search(query: str) -> str:
    """Get web search results for a query."""
    if not settings.tavily_api_key:
        return "TAVILY_API_KEY is not configured."
    if TavilyClient is None:
        return "TavilyClient is not installed."

    try:
        client = TavilyClient(settings.tavily_api_key)
        response = client.search(query=query, search_depth="advanced")
        return str(response)
    except Exception as exc:
        return f"web search failed: {exc}"
