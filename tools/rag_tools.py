"""
tools/rag_tools.py
RAG (Retrieval-Augmented Generation) tools using ChromaDB.
Includes a sample customer support knowledge base.
"""
import os
from langchain_core.tools import tool

# Optional heavy deps — graceful fallback
try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import SentenceTransformerEmbeddings
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# ─── Sample knowledge base documents ────────────────────────────────────────
SAMPLE_KNOWLEDGE_BASE = [
    {
        "content": "To reset your password: Go to login page → click 'Forgot Password' → enter your email → check inbox for reset link → follow the link and set a new password. The link expires in 24 hours.",
        "metadata": {"category": "account", "topic": "password_reset"},
    },
    {
        "content": "Subscription plans: Basic ($9/mo) - 5 users, 10GB storage. Pro ($29/mo) - 25 users, 100GB storage, priority support. Enterprise ($99/mo) - unlimited users, 1TB storage, dedicated support manager.",
        "metadata": {"category": "billing", "topic": "pricing"},
    },
    {
        "content": "Refund policy: We offer full refunds within 30 days of purchase. After 30 days, pro-rated refunds are available. To request a refund, contact support@example.com with your order ID.",
        "metadata": {"category": "billing", "topic": "refunds"},
    },
    {
        "content": "Our API rate limits: Free tier: 100 requests/hour. Basic: 1,000 requests/hour. Pro: 10,000 requests/hour. Enterprise: unlimited. Rate limits reset every hour on the hour.",
        "metadata": {"category": "technical", "topic": "api_limits"},
    },
    {
        "content": "Data export: Go to Settings → Data Management → Export Data. You can export in CSV or JSON format. Large exports are sent via email. Exports include all user data, transactions, and logs.",
        "metadata": {"category": "technical", "topic": "data_export"},
    },
    {
        "content": "Two-factor authentication (2FA): Enable in Security Settings. We support authenticator apps (Google Authenticator, Authy) and SMS. Backup codes are provided when you enable 2FA. Store them safely.",
        "metadata": {"category": "security", "topic": "2fa"},
    },
    {
        "content": "Integrations supported: Slack, Zapier, GitHub, Google Workspace, Microsoft 365, Salesforce, HubSpot, Stripe. Setup guides are available in our documentation at docs.example.com/integrations.",
        "metadata": {"category": "technical", "topic": "integrations"},
    },
    {
        "content": "Team management: Owners can add/remove members, assign roles (Admin, Member, Viewer), and set permissions per workspace. Go to Settings → Team to manage your team.",
        "metadata": {"category": "account", "topic": "team_management"},
    },
    {
        "content": "Support hours: Live chat is available Monday-Friday 9am-6pm EST. Email support is 24/7 with response within 4 hours for Pro/Enterprise. Check status.example.com for system status.",
        "metadata": {"category": "support", "topic": "contact"},
    },
    {
        "content": "Mobile app: Available on iOS (App Store) and Android (Google Play). Search for 'ExampleApp'. The mobile app supports all core features. Offline mode is available for Pro and Enterprise plans.",
        "metadata": {"category": "technical", "topic": "mobile_app"},
    },
]

_vectorstore = None
_CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", ".chroma_db")


def get_vectorstore():
    """Lazily initialize and return the ChromaDB vector store."""
    if not RAG_AVAILABLE:
        raise RuntimeError("chromadb/sentence-transformers not installed. Run: pip install chromadb sentence-transformers")
    global _vectorstore
    if _vectorstore is None:
        embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        chroma_path = os.path.abspath(_CHROMA_DIR)
        
        # Check if DB already exists
        if os.path.exists(chroma_path) and os.listdir(chroma_path):
            _vectorstore = Chroma(
                persist_directory=chroma_path,
                embedding_function=embeddings,
                collection_name="support_kb",
            )
        else:
            # Create and populate the knowledge base
            texts = [doc["content"] for doc in SAMPLE_KNOWLEDGE_BASE]
            metadatas = [doc["metadata"] for doc in SAMPLE_KNOWLEDGE_BASE]
            _vectorstore = Chroma.from_texts(
                texts=texts,
                metadatas=metadatas,
                embedding=embeddings,
                persist_directory=chroma_path,
                collection_name="support_kb",
            )
            print("✅ Knowledge base initialized with sample documents.")
    return _vectorstore


@tool
def search_knowledge_base(query: str, k: int = 3) -> str:
    """
    Search the customer support knowledge base for relevant information.
    Returns the top matching documents with similarity scores.
    """
    try:
        vs = get_vectorstore()
        docs = vs.similarity_search_with_score(query, k=k)
        if not docs:
            return "No relevant information found in the knowledge base."
        
        results = []
        for i, (doc, score) in enumerate(docs, 1):
            confidence = "High" if score < 0.5 else "Medium" if score < 0.8 else "Low"
            category = doc.metadata.get("category", "general")
            results.append(
                f"[Result {i} | Confidence: {confidence} | Category: {category}]\n{doc.page_content}"
            )
        return "\n\n---\n\n".join(results)
    except Exception as e:
        return f"Knowledge base search failed: {e}"


@tool
def add_to_knowledge_base(content: str, category: str = "general", topic: str = "misc") -> str:
    """
    Add a new document to the customer support knowledge base.
    Useful for expanding the knowledge base with new information.
    """
    try:
        vs = get_vectorstore()
        vs.add_texts(
            texts=[content],
            metadatas=[{"category": category, "topic": topic}],
        )
        return f"✅ Successfully added to knowledge base under category '{category}', topic '{topic}'."
    except Exception as e:
        return f"Failed to add document: {e}"
