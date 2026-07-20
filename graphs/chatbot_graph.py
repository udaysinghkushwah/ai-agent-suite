"""
graphs/chatbot_graph.py
LangGraph graph for a conversational chatbot with persistent memory.
Uses LangGraph's MemorySaver for multi-turn conversation history.
"""
from typing import TypedDict, Annotated, List
import operator
from datetime import datetime
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from config.settings import get_llm, CHATBOT_SYSTEM
from tools.search_tools import web_search, search_wikipedia


# ─── Extra tools ─────────────────────────────────────────────────────────────
from langchain_core.tools import tool

@tool
def get_current_datetime() -> str:
    """Get the current date and time."""
    return datetime.now().strftime("Date: %A, %B %d, %Y | Time: %I:%M %p")

@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely. Example: '2 + 2 * 10'"""
    try:
        # Safe evaluation - only allow math operations
        allowed_names = {"__builtins__": {}}
        import math
        allowed_names.update({k: getattr(math, k) for k in dir(math) if not k.startswith("_")})
        result = eval(expression, allowed_names)  # noqa: S307
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {e}"


CHATBOT_TOOLS = [web_search, search_wikipedia, get_current_datetime, calculator]


# ─── State ──────────────────────────────────────────────────────────────────

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


# ─── Nodes ──────────────────────────────────────────────────────────────────

def chat_node(state: ChatState) -> dict:
    """Main LLM node — decides whether to respond or call a tool."""
    llm = get_llm(temperature=0.7)
    llm_with_tools = llm.bind_tools(CHATBOT_TOOLS)
    
    messages = [CHATBOT_SYSTEM] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def should_continue(state: ChatState) -> str:
    """Route to tools if tool calls present, else end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


# ─── Graph Builder ───────────────────────────────────────────────────────────

def build_chatbot_graph() -> StateGraph:
    builder = StateGraph(ChatState)
    
    tool_node = ToolNode(CHATBOT_TOOLS)
    
    builder.add_node("chat", chat_node)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "chat")
    builder.add_conditional_edges("chat", should_continue, {"tools": "tools", END: END})
    builder.add_edge("tools", "chat")  # Loop back after tool use

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# ─── Convenience runner ──────────────────────────────────────────────────────

def chat(message: str, thread_id: str = "chat-session-1", graph=None) -> str:
    """Send a message and get a response (with memory per thread_id)."""
    if graph is None:
        graph = build_chatbot_graph()
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke({"messages": [HumanMessage(content=message)]}, config)
    return result["messages"][-1].content


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    graph = build_chatbot_graph()
    thread = "demo-chat"
    
    print("\n💬 Chatbot Ready! (type 'quit' to exit)\n" + "="*50)
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if not user_input:
            continue
        response = chat(user_input, thread_id=thread, graph=graph)
        print(f"\n🤖 Assistant: {response}")
