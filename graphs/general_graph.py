"""
graphs/general_graph.py
LangGraph ReAct (Reason + Act) graph for the General Purpose Agent.
Standard ReAct loop: Think → Act (tool call) → Observe → Repeat until done.
"""
from typing import TypedDict, Annotated, List, Literal
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from config.settings import get_llm, GENERAL_SYSTEM
from tools.search_tools import web_search, search_wikipedia


# ─── Additional General-Purpose Tools ───────────────────────────────────────

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression. Example inputs: '2**10', 'sqrt(144)', '100 * 0.15'"""
    import math
    try:
        safe_globals = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_globals["__builtins__"] = {}
        result = eval(expression, safe_globals)  # noqa: S307
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


@tool
def get_current_datetime() -> str:
    """Get the current date and time in a human-readable format."""
    from datetime import datetime
    now = datetime.now()
    return (
        f"Current Date: {now.strftime('%A, %B %d, %Y')}\n"
        f"Current Time: {now.strftime('%I:%M %p')}\n"
        f"Timestamp: {now.isoformat()}"
    )


@tool
def word_count(text: str) -> str:
    """Count words, characters, and sentences in a given text."""
    words = len(text.split())
    chars = len(text)
    sentences = text.count(".") + text.count("!") + text.count("?")
    return f"Words: {words} | Characters: {chars} | Sentences: {sentences}"


@tool
def python_repl(code: str) -> str:
    """
    Execute simple Python code in a safe sandbox.
    Use for data processing, list manipulation, string formatting, etc.
    Do NOT use for file system operations or network requests.
    """
    import io
    import contextlib
    safe_globals = {
        "__builtins__": {
            "print": print, "len": len, "range": range, "enumerate": enumerate,
            "list": list, "dict": dict, "set": set, "tuple": tuple, "str": str,
            "int": int, "float": float, "bool": bool, "sum": sum, "min": min,
            "max": max, "sorted": sorted, "reversed": reversed, "zip": zip,
            "map": map, "filter": filter, "abs": abs, "round": round,
        }
    }
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            exec(code, safe_globals)  # noqa: S102
        result = output.getvalue()
        return result if result else "Code executed successfully (no output)."
    except Exception as e:
        return f"Execution error: {type(e).__name__}: {e}"


GENERAL_TOOLS = [web_search, search_wikipedia, calculator, get_current_datetime, word_count, python_repl]


# ─── State ──────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


# ─── Nodes ──────────────────────────────────────────────────────────────────

def agent_node(state: AgentState) -> dict:
    """Core ReAct agent node — reasons and decides whether to use tools."""
    llm = get_llm(temperature=0.5)
    llm_with_tools = llm.bind_tools(GENERAL_TOOLS)
    
    messages = [GENERAL_SYSTEM] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Check if the last message has tool calls."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ─── Graph Builder ───────────────────────────────────────────────────────────

def build_general_graph() -> StateGraph:
    builder = StateGraph(AgentState)
    
    tool_node = ToolNode(GENERAL_TOOLS)
    
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "agent")

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# ─── Convenience runner ──────────────────────────────────────────────────────

def run_agent(query: str, thread_id: str = "general-1", graph=None) -> str:
    """Run the general purpose agent on a query."""
    if graph is None:
        graph = build_general_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"messages": [HumanMessage(content=query)]}, config)
    return result["messages"][-1].content


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    graph = build_general_graph()
    thread = "general-demo"
    
    test_queries = [
        "What is 15% of 847? Show your work.",
        "What are the latest developments in quantum computing?",
        "Write me a Python function to reverse a string, then run it with the input 'Hello, World!'",
    ]
    
    print("\n⚡ General Purpose Agent\n" + "="*50)
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        response = run_agent(query, thread_id=thread, graph=graph)
        print(f"🤖 Response: {response}\n" + "-"*40)
