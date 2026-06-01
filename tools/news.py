import chromadb
from langchain_core.tools import tool

from config.settings import VECDB_PATH


@tool
def news_search_tool(company: str):
    """Search recent news about a company from the ChromaDB vector store."""
    chroma_client = chromadb.PersistentClient(path=VECDB_PATH)
    collection = chroma_client.get_or_create_collection(name="news_collection")
    results = collection.query(
        query_texts=[f"the most recent news about {company}"],
        n_results=5,
    )
    return results["documents"][0] if results and results["documents"] else []
