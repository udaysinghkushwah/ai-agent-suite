"""
config/settings.py
Shared configuration, LangSmith setup, and LLM factory for all agents.
"""
import os
from functools import lru_cache
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage

load_dotenv()


# ─── LangSmith tracing is auto-configured via env vars ─────────────────────
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=...
# LANGCHAIN_PROJECT=ai-agent-suite
# ────────────────────────────────────────────────────────────────────────────


def validate_env() -> None:
    """Ensure required API keys are set before running any agent."""
    missing = []
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not os.getenv("LANGCHAIN_API_KEY"):
        missing.append("LANGCHAIN_API_KEY (for LangSmith tracing)")
    if missing:
        raise EnvironmentError(
            f"\n❌ Missing required environment variables:\n"
            + "\n".join(f"  • {k}" for k in missing)
            + "\n\nCopy .env.example to .env and fill in your keys."
        )


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.7) -> ChatAnthropic:
    """Return a cached ChatAnthropic instance."""
    validate_env()
    return ChatAnthropic(
        model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
        max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
        temperature=temperature,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    )


# ─── Shared system prompts ──────────────────────────────────────────────────

RESEARCH_SYSTEM = SystemMessage(content="""You are an expert research assistant.
Your job is to gather information, synthesize findings, and produce clear,
well-structured research reports. Always cite your sources.""")

CHATBOT_SYSTEM = SystemMessage(content="""You are a helpful, friendly AI assistant
with access to various tools. Be concise, accurate, and engaging. Remember the
conversation history and refer to it naturally.""")

SUPPORT_SYSTEM = SystemMessage(content="""You are a professional customer support
agent. Use the knowledge base to answer questions accurately. If you cannot find
a confident answer, escalate politely. Be empathetic and solution-focused.""")

CODE_REVIEW_SYSTEM = SystemMessage(content="""You are an expert software engineer
performing code reviews. Analyze code for correctness, style, performance, and
security issues. Provide actionable, constructive feedback with severity ratings.""")

GENERAL_SYSTEM = SystemMessage(content="""You are a versatile AI assistant with
access to powerful tools. Use them thoughtfully to answer questions and complete
tasks. Think step-by-step before acting.""")
