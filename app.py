"""
app.py
Unified Streamlit dashboard for the AI Agent Suite.
Run with: streamlit run app.py
"""
import os
import sys
import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Agent Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a0f2e 50%, #0f1a2e 100%); }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.3);
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.2rem;
    font-weight: 700;
    color: white;
    margin: 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    color: rgba(255,255,255,0.85);
    font-size: 1.05rem;
    margin-top: 0.4rem;
    font-weight: 300;
}
.hero-badges {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
    flex-wrap: wrap;
}
.badge {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.78rem;
    color: white;
    font-weight: 500;
}

/* Agent cards */
.agent-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.2rem;
    margin: 0.5rem 0;
    transition: all 0.3s ease;
    cursor: pointer;
}
.agent-card:hover {
    background: rgba(99,102,241,0.1);
    border-color: rgba(99,102,241,0.4);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99,102,241,0.15);
}

/* Status indicators */
.status-online {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #22c55e;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
    70% { box-shadow: 0 0 0 6px rgba(34,197,94,0); }
    100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}

/* Output area */
.output-container {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.5rem;
    font-family: 'Inter', sans-serif;
    color: rgba(255,255,255,0.9);
    line-height: 1.7;
    max-height: 600px;
    overflow-y: auto;
}

/* Info panels */
.info-panel {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
}

/* Streamlit overrides */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(99,102,241,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.4) !important;
}
.stTextArea textarea, .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: white !important;
}
.stSidebar { background: rgba(0,0,0,0.3) !important; border-right: 1px solid rgba(255,255,255,0.05) !important; }
.stChatMessage { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 12px !important; }

/* Metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.75rem;
    margin: 1rem 0;
}
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-value { font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
.metric-label { font-size: 0.75rem; color: rgba(255,255,255,0.5); margin-top: 0.2rem; }

/* Divider */
.custom-divider { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ──────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_graph" not in st.session_state:
    st.session_state.chat_graph = None
if "general_graph" not in st.session_state:
    st.session_state.general_graph = None
if "thread_counter" not in st.session_state:
    st.session_state.thread_counter = 0


def check_env() -> bool:
    """Check if required env vars are set."""
    return bool(os.getenv("ANTHROPIC_API_KEY")) and bool(os.getenv("LANGCHAIN_API_KEY"))


def env_warning():
    st.error("""
    ⚠️ **Missing API Keys!** Copy `.env.example` to `.env` and add your keys:
    - `ANTHROPIC_API_KEY` (from console.anthropic.com)
    - `LANGCHAIN_API_KEY` (from smith.langchain.com)
    """)


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size:2.5rem;">🤖</div>
        <div style="font-size:1.1rem; font-weight:700; color:white;">AI Agent Suite</div>
        <div style="font-size:0.75rem; color:rgba(255,255,255,0.5);">Powered by Claude + LangGraph</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    agent_choice = st.selectbox(
        "🎯 Select Agent",
        options=[
            "🏠 Dashboard",
            "🔍 Research Assistant",
            "💬 Conversational Chatbot",
            "🧑‍💼 Customer Support",
            "🛠️ Code Review",
            "⚡ General Purpose ReAct",
        ],
        key="agent_select"
    )
    
    st.divider()
    
    # Status panel
    anthropic_ok = bool(os.getenv("ANTHROPIC_API_KEY"))
    langsmith_ok = bool(os.getenv("LANGCHAIN_API_KEY"))
    
    st.markdown("**🔌 Connection Status**")
    st.markdown(f"{'✅' if anthropic_ok else '❌'} Anthropic Claude")
    st.markdown(f"{'✅' if langsmith_ok else '❌'} LangSmith Tracing")
    tavily_ok = bool(os.getenv("TAVILY_API_KEY")) and os.getenv("TAVILY_API_KEY") != "your_tavily_api_key_here"
    st.markdown(f"{'✅' if tavily_ok else '⚠️'} Tavily Search {'(active)' if tavily_ok else '(using DuckDuckGo)'}")
    
    st.divider()
    st.markdown("""
    <div style="font-size:0.72rem; color:rgba(255,255,255,0.35); text-align:center;">
    All runs traced in LangSmith<br>
    <a href="https://smith.langchain.com" target="_blank" style="color:#8b5cf6;">View Dashboard →</a>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("""
    <div style="text-align:center; margin-bottom: 0.5rem;">
        <span style="font-size:0.9rem; font-weight:600; color:white;">☕ Buy Me a Coffee</span>
    </div>
    """, unsafe_allow_html=True)
    import os
    if os.path.exists("assets/upi-qr.jpg"):
        st.image("assets/upi-qr.jpg", caption="Scan via UPI to support!", use_container_width=True)
    else:
        st.info("💡 Place your `upi-qr.jpg` in the `assets/` folder to display your QR code here.")



# ─── Hero Banner ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🤖 AI Agent Suite</div>
    <div class="hero-subtitle">5 specialized AI agents powered by LangChain · LangGraph · LangSmith</div>
    <div class="hero-badges">
        <span class="badge">⚡ LangGraph Workflows</span>
        <span class="badge">🔗 LangChain Tools</span>
        <span class="badge">📊 LangSmith Tracing</span>
        <span class="badge">🧠 Claude claude-3-5-sonnet</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if agent_choice == "🏠 Dashboard":
    st.markdown("## 👋 Welcome to the AI Agent Suite")
    st.markdown("Select an agent from the sidebar to get started. Here's what each agent can do:")
    
    agents_info = [
        ("🔍", "Research Assistant", "Multi-step research: Plan → Web Search → Synthesize → Report",
         "Ask it to research any topic and get a structured report.", "#6366f1"),
        ("💬", "Conversational Chatbot", "Memory-aware multi-turn chat with tools",
         "Persistent conversation with web search, calculator, and more.", "#8b5cf6"),
        ("🧑‍💼", "Customer Support", "RAG-powered support with escalation routing",
         "Answers from a knowledge base, auto-escalates low-confidence answers.", "#06b6d4"),
        ("🛠️", "Code Review", "Static analysis + AI review pipeline",
         "Paste any Python code and get a full review with severity ratings.", "#f59e0b"),
        ("⚡", "General ReAct", "Flexible ReAct agent with 6 tools",
         "Web search, math, Python REPL, Wikipedia, and more.", "#22c55e"),
    ]
    
    col1, col2 = st.columns(2)
    for i, (emoji, name, tagline, description, color) in enumerate(agents_info):
        col = col1 if i % 2 == 0 else col2
        with col:
            st.markdown(f"""
            <div class="agent-card">
                <div style="font-size:1.8rem;">{emoji}</div>
                <div style="font-size:1rem; font-weight:600; color:white; margin-top:0.3rem;">{name}</div>
                <div style="font-size:0.78rem; color:{color}; margin-top:0.2rem;">{tagline}</div>
                <div style="font-size:0.82rem; color:rgba(255,255,255,0.6); margin-top:0.5rem;">{description}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Tech stack info
    st.markdown("### 🛠️ Technology Stack")
    tech_col1, tech_col2, tech_col3 = st.columns(3)
    
    with tech_col1:
        st.markdown("""
        **🔗 LangChain**
        - Tool definitions
        - LLM integration
        - Prompt templates
        - Chain composition
        """)
    
    with tech_col2:
        st.markdown("""
        **📊 LangGraph**
        - Stateful workflows
        - Conditional routing
        - Memory persistence
        - ReAct loops
        """)
    
    with tech_col3:
        st.markdown("""
        **🔍 LangSmith**
        - Full run tracing
        - Step-by-step logs
        - Latency tracking
        - Error debugging
        """)
    
    st.info("💡 **Tip:** Every agent run is automatically traced in LangSmith. Open [smith.langchain.com](https://smith.langchain.com) to see full execution traces.")

    st.divider()
    coffee_col1, coffee_col2 = st.columns([1, 4])
    with coffee_col1:
        import os
        if os.path.exists("assets/upi-qr.jpg"):
            st.image("assets/upi-qr.jpg", width=140, caption="UPI QR Code")
        else:
            st.warning("⚠️ QR code image missing in assets/")
    with coffee_col2:
        st.markdown("""
        ### ☕ Buy Me a Coffee
        If you find this suite of AI agents useful, feel free to support my work by buying me a coffee. 
        Scan the QR code using any UPI app. Thank you for your support!
        """)


# ══════════════════════════════════════════════════════════════════════════════
# 1. RESEARCH ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
elif agent_choice == "🔍 Research Assistant":
    st.markdown("## 🔍 Research Assistant")
    st.markdown("Enter a topic and get a comprehensive, multi-source research report.")
    
    if not check_env():
        env_warning()
        st.stop()
    
    with st.expander("ℹ️ How it works", expanded=False):
        st.markdown("""
        **LangGraph Flow:**
        1. **Planner** — Generates 3–5 targeted search queries
        2. **Searcher** — Executes web searches + Wikipedia lookup
        3. **Summarizer** — Synthesizes all results into key findings
        4. **Report Writer** — Produces a structured markdown report
        """)
    
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g., The future of quantum computing in cryptography",
        help="Be specific for better results",
    )
    
    col_btn, col_ex = st.columns([1, 3])
    with col_btn:
        run_research = st.button("🚀 Start Research", use_container_width=True)
    with col_ex:
        example_topics = [
            "Impact of AI on healthcare in 2024",
            "Climate change mitigation technologies",
            "The history and future of space exploration",
        ]
        if st.button("🎲 Random Example", use_container_width=False):
            import random
            st.session_state["research_topic_example"] = random.choice(example_topics)
            st.rerun()
    
    if "research_topic_example" in st.session_state and not topic:
        topic = st.session_state["research_topic_example"]
    
    if run_research and topic.strip():
        from graphs.research_graph import build_research_graph
        
        progress_placeholder = st.empty()
        steps = ["📋 Planning queries...", "🔍 Searching the web...", "📝 Synthesizing results...", "✍️ Writing report..."]
        
        graph = build_research_graph()
        config = {"configurable": {"thread_id": f"research-{int(time.time())}"}}
        
        with st.spinner(""):
            result_container = st.empty()
            step_texts = []
            
            for step_idx, (event_key, event_val) in enumerate(graph.stream(
                {"topic": topic, "queries": [], "search_results": [], "summary": "", "report": "", "messages": []},
                config, stream_mode="updates"
            )):
                node_name = list(event_key.keys())[0] if isinstance(event_key, dict) else str(event_key)
                step_label = steps[min(step_idx, len(steps)-1)]
                
                progress_placeholder.markdown(f"""
                <div class="info-panel">
                    <span class="status-online"></span> 
                    <strong>{step_label}</strong>
                </div>
                """, unsafe_allow_html=True)
        
        # Fetch final state
        final = graph.get_state(config)
        report = final.values.get("report", "No report generated.")
        
        progress_placeholder.empty()
        st.success("✅ Research complete! Traces available in LangSmith.")
        st.markdown(report)
        
        st.download_button(
            "📥 Download Report",
            data=report,
            file_name=f"research_{topic[:30].replace(' ', '_')}.md",
            mime="text/markdown",
        )
    elif run_research:
        st.warning("Please enter a research topic.")


# ══════════════════════════════════════════════════════════════════════════════
# 2. CONVERSATIONAL CHATBOT
# ══════════════════════════════════════════════════════════════════════════════
elif agent_choice == "💬 Conversational Chatbot":
    st.markdown("## 💬 Conversational Chatbot")
    st.markdown("Multi-turn AI chat with memory. The bot remembers everything in this session.")
    
    if not check_env():
        env_warning()
        st.stop()
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.session_state.thread_counter += 1
            st.session_state.chat_graph = None
            st.rerun()
    
    # Init graph
    if st.session_state.chat_graph is None:
        from graphs.chatbot_graph import build_chatbot_graph
        st.session_state.chat_graph = build_chatbot_graph()
    
    # Chat history display
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Input
    if user_input := st.chat_input("Message the chatbot..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                from graphs.chatbot_graph import chat
                thread_id = f"chatbot-{st.session_state.thread_counter}"
                response = chat(user_input, thread_id=thread_id, graph=st.session_state.chat_graph)
            st.markdown(response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
    
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="info-panel">
        💡 <strong>Try asking:</strong> "What's 15% of 847?", "Search for latest AI news", "What time is it?", or anything else!
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 3. CUSTOMER SUPPORT
# ══════════════════════════════════════════════════════════════════════════════
elif agent_choice == "🧑‍💼 Customer Support":
    st.markdown("## 🧑‍💼 Customer Support Agent")
    st.markdown("RAG-powered support agent. Answers from a knowledge base, auto-escalates uncertain queries.")
    
    if not check_env():
        env_warning()
        st.stop()
    
    with st.expander("📚 Knowledge Base Topics", expanded=False):
        st.markdown("""
        The knowledge base contains information about:
        - 🔑 Password reset & account management
        - 💳 Billing, subscriptions & refund policy
        - 🔒 Two-factor authentication (2FA) setup
        - 🔌 API rate limits & integrations
        - 📱 Mobile app & data export
        - 👥 Team management & permissions
        - 🕐 Support hours & contact info
        """)
    
    query = st.text_area(
        "Customer Query",
        placeholder="e.g., How do I reset my password? What is the refund policy?",
        height=100,
    )
    
    example_queries = [
        "How do I reset my password?",
        "What's the difference between Basic and Pro plans?",
        "Can I get a refund?",
        "How do I enable two-factor authentication?",
        "What are the API rate limits?",
    ]
    
    selected_example = st.selectbox("Or try an example query:", ["-- Select --"] + example_queries)
    if selected_example != "-- Select --":
        query = selected_example
    
    if st.button("🎧 Get Support Answer", use_container_width=False) and query.strip():
        with st.spinner("🔍 Searching knowledge base..."):
            from graphs.support_graph import answer_support_query
            result = answer_support_query(query, thread_id=f"support-{int(time.time())}")
        
        # Confidence indicator
        confidence_colors = {"high": "#22c55e", "medium": "#f59e0b", "low": "#ef4444"}
        conf_color = confidence_colors.get(result["confidence"], "#6b7280")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🏷️ Intent", result["intent"].title())
        col2.metric("📊 Confidence", result["confidence"].title())
        col3.metric("🚨 Escalated", "Yes" if result["escalated"] else "No")
        
        st.divider()
        st.markdown("### 💬 Support Response")
        st.markdown(result["answer"])
        
        if result["escalated"]:
            st.warning("⚠️ This query has been flagged for human agent follow-up due to low confidence.")
        else:
            st.success("✅ Query resolved by AI agent.")
    elif st.button("🎧 Get Support Answer", use_container_width=False):
        st.warning("Please enter a query.")


# ══════════════════════════════════════════════════════════════════════════════
# 4. CODE REVIEW
# ══════════════════════════════════════════════════════════════════════════════
elif agent_choice == "🛠️ Code Review":
    st.markdown("## 🛠️ Code Review Agent")
    st.markdown("Paste your Python code for a full AI-powered review: syntax, lint, security, complexity, and AI feedback.")
    
    if not check_env():
        env_warning()
        st.stop()
    
    col1, col2 = st.columns([4, 1])
    with col2:
        language = st.selectbox("Language", ["python", "javascript", "typescript", "other"])
    
    sample_code = '''def authenticate_user(username, password="admin123"):
    """Authenticate a user."""
    import pickle, os
    
    # Load users from pickle file
    if os.path.exists("users.pkl"):
        users = pickle.loads(open("users.pkl", "rb").read())
    
    # Check credentials
    query = f"SELECT * FROM users WHERE username=\'{username}\'"
    
    if username == "admin" and password == "admin123":
        session_token = eval(f"generate_token(\'{username}\')")
        return {"token": session_token, "role": "admin"}
    
    return None

def process_items(items):
    result = []
    for i in range(len(items)):
        for j in range(len(items)):
            if items[i] > items[j]:
                result.append(items[i])
    return result
'''
    
    code_input = st.text_area(
        "Paste your code here",
        value=sample_code,
        height=300,
        help="Paste Python code to review",
    )
    
    if st.button("🔍 Run Code Review", use_container_width=False) and code_input.strip():
        with st.spinner("🔬 Analyzing code..."):
            steps_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            steps_done = ["Parsing syntax...", "Running linter...", "Scanning security...", "Measuring complexity...", "AI reviewing...", "Generating report..."]
            for i, step in enumerate(steps_done):
                steps_placeholder.info(f"⏳ {step}")
                progress_bar.progress((i + 1) / len(steps_done))
                time.sleep(0.1)
            
            from graphs.code_graph import review_code
            report = review_code(code_input, language=language, thread_id=f"review-{int(time.time())}")
        
        steps_placeholder.empty()
        progress_bar.empty()
        
        st.success("✅ Code review complete!")
        st.markdown(report)
        
        st.download_button(
            "📥 Download Review",
            data=report,
            file_name="code_review.md",
            mime="text/markdown",
        )


# ══════════════════════════════════════════════════════════════════════════════
# 5. GENERAL PURPOSE REACT AGENT
# ══════════════════════════════════════════════════════════════════════════════
elif agent_choice == "⚡ General Purpose ReAct":
    st.markdown("## ⚡ General Purpose ReAct Agent")
    st.markdown("A flexible agent with 6 tools. Ask anything — it reasons, uses tools, and delivers results.")
    
    if not check_env():
        env_warning()
        st.stop()
    
    with st.expander("🧰 Available Tools", expanded=False):
        tools_info = {
            "🔍 web_search": "Search the web for current information",
            "📖 search_wikipedia": "Search Wikipedia for factual info",
            "🔢 calculator": "Evaluate math expressions (supports sqrt, sin, log, etc.)",
            "🕐 get_current_datetime": "Get current date and time",
            "📝 word_count": "Count words, characters, and sentences in text",
            "🐍 python_repl": "Execute safe Python code snippets",
        }
        for tool_name, desc in tools_info.items():
            st.markdown(f"**{tool_name}** — {desc}")
    
    # Init graph
    if st.session_state.general_graph is None:
        from graphs.general_graph import build_general_graph
        st.session_state.general_graph = build_general_graph()
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🆕 New Thread"):
            st.session_state.thread_counter += 1
            st.session_state.general_graph = None
            st.rerun()
    
    st.markdown(f"**Thread:** `general-{st.session_state.thread_counter}`")
    
    example_queries = [
        "What is 15% tip on a $127.50 restaurant bill?",
        "Search for the latest news about artificial intelligence",
        "Write a Python function to check if a number is prime, then test it with 17 and 20",
        "What day of the week is today, and how many days until New Year?",
        "Count the words in: 'The quick brown fox jumps over the lazy dog'",
    ]
    
    selected_example = st.selectbox("💡 Try an example:", ["-- Custom query --"] + example_queries)
    
    query = st.text_input(
        "Your query",
        value=selected_example if selected_example != "-- Custom query --" else "",
        placeholder="Ask the agent anything...",
    )
    
    if st.button("⚡ Run Agent", use_container_width=False) and query.strip():
        with st.spinner("🤔 Agent is thinking and acting..."):
            from graphs.general_graph import run_agent
            thread_id = f"general-{st.session_state.thread_counter}"
            response = run_agent(query, thread_id=thread_id, graph=st.session_state.general_graph)
        
        st.success("✅ Done!")
        st.markdown("### 💬 Agent Response")
        st.markdown(response)
