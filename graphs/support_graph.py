"""
graphs/support_graph.py
LangGraph graph for the RAG-powered Customer Support agent.

Flow: Classify Intent → Retrieve from KB → Generate Answer → Confidence Check → Escalate if needed
"""
from typing import TypedDict, Annotated, List, Literal
import operator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from config.settings import get_llm, SUPPORT_SYSTEM
try:
    from tools.rag_tools import search_knowledge_base
    RAG_READY = True
except Exception:
    RAG_READY = False
    def search_knowledge_base(query, k=3):  # type: ignore
        return "⚠️ Knowledge base not available (install chromadb + sentence-transformers to enable RAG)."


# ─── State ──────────────────────────────────────────────────────────────────

class SupportState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    user_query: str
    intent: str
    retrieved_docs: str
    answer: str
    confidence: str   # "high", "medium", "low"
    escalate: bool


# ─── Nodes ──────────────────────────────────────────────────────────────────

def intent_classifier_node(state: SupportState) -> dict:
    """Classify user intent into a support category."""
    llm = get_llm(temperature=0.1)
    response = llm.invoke([
        HumanMessage(content=(
            f"Classify this customer support query into ONE category: "
            f"[billing, account, technical, security, general]\n\n"
            f"Query: {state['user_query']}\n\n"
            "Return ONLY the category word, nothing else."
        ))
    ])
    intent = response.content.strip().lower()
    valid_intents = {"billing", "account", "technical", "security", "general"}
    intent = intent if intent in valid_intents else "general"
    return {
        "intent": intent,
        "messages": [AIMessage(content=f"🏷️ Intent classified: **{intent}**")],
    }


def retriever_node(state: SupportState) -> dict:
    """Retrieve relevant documents from the knowledge base."""
    enhanced_query = f"{state['user_query']} {state['intent']}"
    try:
        docs = search_knowledge_base.invoke({"query": enhanced_query, "k": 3})
    except Exception as e:
        docs = f"Knowledge base unavailable: {e}"
    return {
        "retrieved_docs": docs,
        "messages": [AIMessage(content="📚 Knowledge base searched.")],
    }


def answer_generator_node(state: SupportState) -> dict:
    """Generate a support answer from retrieved documents."""
    llm = get_llm(temperature=0.3)
    response = llm.invoke([
        SUPPORT_SYSTEM,
        HumanMessage(content=(
            f"Customer Query: {state['user_query']}\n"
            f"Intent Category: {state['intent']}\n\n"
            f"Knowledge Base Results:\n{state['retrieved_docs']}\n\n"
            "Provide a helpful, accurate, empathetic support response. "
            "If the knowledge base has a clear answer, use it. "
            "At the end of your response, on a new line, add exactly one of: "
            "[CONFIDENCE: HIGH], [CONFIDENCE: MEDIUM], or [CONFIDENCE: LOW] "
            "based on how confident you are in your answer."
        ))
    ])
    
    content = response.content
    confidence = "medium"
    
    if "[CONFIDENCE: HIGH]" in content:
        confidence = "high"
        content = content.replace("[CONFIDENCE: HIGH]", "").strip()
    elif "[CONFIDENCE: MEDIUM]" in content:
        confidence = "medium"
        content = content.replace("[CONFIDENCE: MEDIUM]", "").strip()
    elif "[CONFIDENCE: LOW]" in content:
        confidence = "low"
        content = content.replace("[CONFIDENCE: LOW]", "").strip()
    
    return {
        "answer": content,
        "confidence": confidence,
        "messages": [AIMessage(content=content)],
    }


def escalation_check_node(state: SupportState) -> dict:
    """Decide if the query should be escalated to a human agent."""
    should_escalate = state["confidence"] == "low"
    if should_escalate:
        escalation_message = (
            "\n\n---\n⚠️ **This query has been flagged for human review.** "
            "A support specialist will follow up within 4 business hours. "
            "Reference ID: " + f"TICKET-{hash(state['user_query']) % 100000:05d}"
        )
        return {
            "escalate": True,
            "messages": [AIMessage(content=escalation_message)],
        }
    return {"escalate": False}


def route_after_answer(state: SupportState) -> Literal["escalation_check", "__end__"]:
    """Route to escalation check or end based on confidence."""
    return "escalation_check"


# ─── Graph Builder ───────────────────────────────────────────────────────────

def build_support_graph() -> StateGraph:
    builder = StateGraph(SupportState)

    builder.add_node("intent_classifier", intent_classifier_node)
    builder.add_node("retriever", retriever_node)
    builder.add_node("answer_generator", answer_generator_node)
    builder.add_node("escalation_check", escalation_check_node)

    builder.add_edge(START, "intent_classifier")
    builder.add_edge("intent_classifier", "retriever")
    builder.add_edge("retriever", "answer_generator")
    builder.add_edge("answer_generator", "escalation_check")
    builder.add_edge("escalation_check", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# ─── Convenience runner ──────────────────────────────────────────────────────

def answer_support_query(query: str, thread_id: str = "support-1") -> dict:
    """Handle a customer support query and return the response."""
    graph = build_support_graph()
    config = {"configurable": {"thread_id": thread_id}}
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "user_query": query,
        "intent": "",
        "retrieved_docs": "",
        "answer": "",
        "confidence": "medium",
        "escalate": False,
    }
    result = graph.invoke(initial_state, config)
    return {
        "answer": result["answer"],
        "intent": result["intent"],
        "confidence": result["confidence"],
        "escalated": result["escalate"],
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    queries = [
        "How do I reset my password?",
        "What is the refund policy?",
        "I need help with something very unusual and complex.",
    ]
    
    print("\n🎧 Customer Support Agent\n" + "="*50)
    for q in queries:
        print(f"\n❓ Query: {q}")
        result = answer_support_query(q)
        print(f"🏷️  Intent: {result['intent']} | Confidence: {result['confidence']} | Escalated: {result['escalated']}")
        print(f"💬 Answer:\n{result['answer']}\n" + "-"*40)
