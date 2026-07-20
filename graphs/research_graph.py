"""
graphs/research_graph.py
LangGraph state machine for the Research Assistant agent.

Flow: Plan → Search (parallel) → Summarize → Write Report → END
"""
from typing import TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from config.settings import get_llm, RESEARCH_SYSTEM
from tools.search_tools import web_search, search_wikipedia


# ─── State ──────────────────────────────────────────────────────────────────

class ResearchState(TypedDict):
    topic: str
    queries: List[str]
    search_results: Annotated[List[str], operator.add]
    summary: str
    report: str
    messages: Annotated[List, operator.add]


# ─── Nodes ──────────────────────────────────────────────────────────────────

def planner_node(state: ResearchState) -> dict:
    """Generate search queries for the research topic."""
    llm = get_llm(temperature=0.3)
    response = llm.invoke([
        RESEARCH_SYSTEM,
        HumanMessage(content=(
            f"Generate 3-5 specific search queries to research this topic thoroughly: '{state['topic']}'\n"
            "Return ONLY the queries, one per line, no numbering or extra text."
        ))
    ])
    queries = [q.strip() for q in response.content.strip().split("\n") if q.strip()]
    return {
        "queries": queries,
        "messages": [AIMessage(content=f"📋 Generated {len(queries)} search queries:\n" + "\n".join(f"• {q}" for q in queries))],
    }


def searcher_node(state: ResearchState) -> dict:
    """Execute web searches for all queries."""
    results = []
    for query in state["queries"][:4]:  # Limit to 4 queries
        try:
            result = web_search.invoke({"query": query})
            results.append(f"**Query:** {query}\n\n{result}")
        except Exception as e:
            results.append(f"**Query:** {query}\n\nSearch failed: {e}")
    
    # Also search Wikipedia for background
    try:
        wiki_result = search_wikipedia.invoke({"query": state["topic"]})
        results.append(f"**Wikipedia:** {state['topic']}\n\n{wiki_result}")
    except Exception:
        pass
    
    return {
        "search_results": results,
        "messages": [AIMessage(content=f"🔍 Completed {len(results)} searches.")],
    }


def summarizer_node(state: ResearchState) -> dict:
    """Synthesize all search results into a coherent summary."""
    llm = get_llm(temperature=0.3)
    all_results = "\n\n" + "=" * 60 + "\n\n".join(state["search_results"])
    
    response = llm.invoke([
        RESEARCH_SYSTEM,
        HumanMessage(content=(
            f"Topic: {state['topic']}\n\n"
            f"Search Results:\n{all_results[:8000]}\n\n"  # Limit context
            "Synthesize these search results into a concise, factual summary (400-600 words). "
            "Focus on key facts, trends, and insights. Note any contradictions or uncertainties."
        ))
    ])
    return {
        "summary": response.content,
        "messages": [AIMessage(content="📝 Research synthesized.")],
    }


def report_writer_node(state: ResearchState) -> dict:
    """Write a polished final research report."""
    llm = get_llm(temperature=0.5)
    
    response = llm.invoke([
        RESEARCH_SYSTEM,
        HumanMessage(content=(
            f"Write a comprehensive research report on: **{state['topic']}**\n\n"
            f"Based on this research summary:\n{state['summary']}\n\n"
            "Format the report with:\n"
            "# [Title]\n"
            "## Executive Summary\n"
            "## Key Findings\n"
            "## Detailed Analysis\n"
            "## Conclusions\n"
            "## Further Reading\n\n"
            "Make it professional, well-structured, and insightful."
        ))
    ])
    return {
        "report": response.content,
        "messages": [AIMessage(content="✅ Research report complete!")],
    }


# ─── Graph Builder ───────────────────────────────────────────────────────────

def build_research_graph() -> StateGraph:
    builder = StateGraph(ResearchState)

    builder.add_node("planner", planner_node)
    builder.add_node("searcher", searcher_node)
    builder.add_node("summarizer", summarizer_node)
    builder.add_node("report_writer", report_writer_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "searcher")
    builder.add_edge("searcher", "summarizer")
    builder.add_edge("summarizer", "report_writer")
    builder.add_edge("report_writer", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# ─── Convenience runner ──────────────────────────────────────────────────────

def run_research(topic: str, thread_id: str = "research-1") -> str:
    """Run a full research workflow and return the final report."""
    graph = build_research_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"topic": topic, "queries": [], "search_results": [], "summary": "", "report": "", "messages": []}, config)
    return result["report"]


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    topic = "The impact of large language models on software development in 2024"
    print(f"\n🔍 Researching: {topic}\n{'='*60}\n")
    report = run_research(topic)
    print(report)
