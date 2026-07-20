"""
tools/search_tools.py
Web search tools: Tavily (preferred) with DuckDuckGo fallback.
"""
import os
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# ─── DuckDuckGo (always available, no API key needed) ──────────────────────
duckduckgo_search = DuckDuckGoSearchRun(name="web_search")

# ─── Wikipedia ──────────────────────────────────────────────────────────────
wikipedia = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=2000),
    name="wikipedia",
    description="Search Wikipedia for factual information about topics, people, places, and events.",
)


def get_search_tool():
    """Return Tavily if API key is present, else DuckDuckGo."""
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key and tavily_key != "your_tavily_api_key_here":
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            return TavilySearchResults(
                max_results=5,
                name="web_search",
                description="Search the web for current information. Returns structured results with URLs.",
                tavily_api_key=tavily_key,
            )
        except Exception:
            pass
    return duckduckgo_search


@tool
def web_search(query: str) -> str:
    """Search the web for current information about any topic."""
    tool_instance = get_search_tool()
    result = tool_instance.invoke(query)
    if isinstance(result, list):
        return "\n\n".join(
            f"[{i+1}] {r.get('title','')}\n{r.get('url','')}\n{r.get('content','')}"
            for i, r in enumerate(result)
        )
    return str(result)


@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for encyclopedic information about a topic."""
    return wikipedia.invoke(query)
