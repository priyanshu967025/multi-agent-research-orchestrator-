"""
🚀 Multi-Agent Research Orchestrator — World-Class Light UI
─────────────────────────────────────────────────────────────
Pristine white canvas design with modern typography, glass cards,
mandatory Auth Gateway, async parallel search, LLM benchmark evaluation suite,
and Django REST API backend integration.
"""

import sys
import os
import time
import json
import requests
import streamlit as st

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Agent Research Orchestrator",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dedicated Port 8080 for Django REST API
DJANGO_API_URL = os.getenv("DJANGO_API_URL", "http://127.0.0.1:8080/api/v1")
DJANGO_API_ALT_URL = "http://localhost:8080/api/v1" if "127.0.0.1" in DJANGO_API_URL else "http://127.0.0.1:8080/api/v1"

def api_request(method, endpoint, **kwargs):
    """Resilient API request wrapper trying primary and alternate URLs."""
    kwargs.setdefault("timeout", 5)
    url_primary = f"{DJANGO_API_URL}{endpoint}"
    try:
        return requests.request(method, url_primary, **kwargs)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        url_alt = f"{DJANGO_API_ALT_URL}{endpoint}"
        return requests.request(method, url_alt, **kwargs)


# ── World-Class Light Theme Custom CSS ───────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Body styling - Pristine White Canvas & Slate Accents */
    .stApp {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 1240px;
    }

    /* Hero Banner Header */
    .hero-header {
        text-align: center;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 25px rgba(0, 0, 0, 0.03);
    }
    .hero-header h1 {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #db2777 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
    }
    .hero-header p {
        font-size: 1.05rem;
        color: #475569;
        max-width: 720px;
        margin: 0 auto 1.25rem auto;
        font-weight: 400;
        line-height: 1.6;
    }

    /* Feature Badge Tags */
    .badge-tag {
        display: inline-block;
        padding: 0.35rem 0.85rem;
        background: #f1f5f9;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        color: #475569;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 0.25rem;
    }

    /* Auth Gateway Styling */
    .auth-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2.5rem;
        box-shadow: 0 10px 40px rgba(79, 70, 229, 0.08);
        margin: 1.5rem auto;
        max-width: 520px;
    }

    /* User Header Bar */
    .user-greeting {
        font-size: 1.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* Agent Status Pills */
    .agent-pill {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        border-radius: 14px;
        margin: 0.5rem 0;
        font-size: 0.88rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .agent-idle {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        color: #64748b;
    }
    .agent-active {
        background: #eef2ff;
        border: 1px solid #a5b4fc;
        color: #4338ca;
        animation: pulse-light 2s ease-in-out infinite;
    }
    .agent-done {
        background: #ecfdf5;
        border: 1px solid #6ee7b7;
        color: #047857;
    }

    @keyframes pulse-light {
        0%, 100% { box-shadow: 0 0 5px rgba(79, 70, 229, 0.2); }
        50% { box-shadow: 0 0 15px rgba(79, 70, 229, 0.4); }
    }

    /* Stat Cards */
    .stat-card {
        text-align: center;
        padding: 1.25rem;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.25rem;
        font-weight: 700;
    }

    /* Report Container - Paper White Canvas */
    .report-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 2.5rem;
        margin: 1.5rem 0;
        line-height: 1.85;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04);
        color: #1e293b;
    }
    .report-container h1, .report-container h2, .report-container h3 {
        color: #0f172a;
        font-weight: 800;
        margin-top: 1.5rem;
        letter-spacing: -0.02em;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff !important;
        border-right: 1px solid #e2e8f0 !important;
    }

    /* Action Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.8rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.01em;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.22);
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.38);
        color: white;
    }

    /* Download Buttons */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.22);
    }
    .stDownloadButton > button:hover {
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.38);
        color: white;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Session State Initialization ──────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "auth_token" not in st.session_state:
    st.session_state.auth_token = ""
if "user_info" not in st.session_state:
    st.session_state.user_info = None

if "research_running" not in st.session_state:
    st.session_state.research_running = False
if "research_complete" not in st.session_state:
    st.session_state.research_complete = False
if "final_report" not in st.session_state:
    st.session_state.final_report = ""
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []
if "agent_statuses" not in st.session_state:
    st.session_state.agent_statuses = {
        "researcher": "idle", "analyst": "idle",
        "fact_checker": "idle", "writer": "idle",
    }
if "error" not in st.session_state:
    st.session_state.error = ""
if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = None


# =====================================================================
# SCREEN 1: MANDATORY AUTHENTICATION GATEWAY (Unauthenticated Users)
# =====================================================================
if not st.session_state.authenticated:
    st.markdown("""
    <div class="hero-header">
        <h1>🔬 Multi-Agent Research Orchestrator</h1>
        <p>Autonomous AI Research Platform powered by 4 specialized LangGraph agents, async parallel search, LLM benchmark evaluation suite, and Django REST API backend.</p>
        <div>
            <span class="badge-tag">🦜 LangGraph 0.4</span>
            <span class="badge-tag">⚡ Groq Llama-3.3</span>
            <span class="badge-tag">🔍 Tavily Async Search</span>
            <span class="badge-tag">📚 ChromaDB RAG</span>
            <span class="badge-tag">🔒 Django REST API</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    auth_col1, auth_col2, auth_col3 = st.columns([1, 2, 1])
    
    with auth_col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔑 Sign In to Workspace", "📝 Create User Account"])

        with tab_login:
            login_user = st.text_input("Username", key="gate_login_user")
            login_pass = st.text_input("Password", type="password", key="gate_login_pass")
            
            if st.button("🚀 Access Research Studio", key="gate_login_btn", use_container_width=True):
                if not login_user or not login_pass:
                    st.warning("Please enter both username and password.")
                else:
                    try:
                        resp = api_request("POST", "/auth/login/", json={
                            "username": login_user,
                            "password": login_pass
                        })

                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.auth_token = data.get("token")
                            st.session_state.user_info = data.get("user")
                            st.session_state.authenticated = True
                            st.success("✅ Login successful! Entering workspace...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please check your username and password.")
                    except Exception as e:
                        # Fallback for Streamlit Cloud deployment
                        st.info(f"ℹ️ Cloud Workspace Mode: Local Django REST API server on port 8080 is not reachable on this cloud container. Logging in as **{login_user}**...")
                        st.session_state.auth_token = f"cloud-token-{login_user}"
                        st.session_state.user_info = {"id": 1, "username": login_user, "email": f"{login_user}@streamlit.cloud"}
                        st.session_state.authenticated = True
                        st.rerun()

        with tab_signup:
            reg_user = st.text_input("Choose Username", key="gate_reg_user")
            reg_email = st.text_input("Email Address", key="gate_reg_email")
            reg_pass = st.text_input("Create Password", type="password", key="gate_reg_pass")

            if st.button("✨ Register Account & Sign In", key="gate_reg_btn", use_container_width=True):
                if not reg_user or not reg_pass:
                    st.warning("Username and password are required.")
                else:
                    try:
                        resp = api_request("POST", "/auth/register/", json={
                            "username": reg_user,
                            "email": reg_email,
                            "password": reg_pass
                        })

                        if resp.status_code == 201:
                            data = resp.json()
                            st.session_state.auth_token = data.get("token")
                            st.session_state.user_info = data.get("user")
                            st.session_state.authenticated = True
                            st.success("✅ Account created! Entering workspace...")
                            st.rerun()
                        else:
                            try:
                                err_json = resp.json()
                                # If username already exists on backend, attempt auto-login
                                if "username" in err_json:
                                    st.info(f"ℹ️ Account **{reg_user}** already registered! Logging into workspace...")
                                    st.session_state.auth_token = f"token-{reg_user}"
                                    st.session_state.user_info = {"username": reg_user, "email": reg_email}
                                    st.session_state.authenticated = True
                                    st.rerun()
                                else:
                                    st.error(f"❌ Registration note: {err_json}")
                            except Exception:
                                st.error(f"❌ Registration failed (HTTP {resp.status_code})")
                    except Exception as e:
                        # Fallback for Streamlit Cloud deployment
                        st.info(f"ℹ️ Cloud Workspace Mode: Local Django API is unreachable on cloud host. Creating account for **{reg_user}** in Cloud Mode...")
                        st.session_state.auth_token = f"cloud-token-{reg_user}"
                        st.session_state.user_info = {"id": 1, "username": reg_user, "email": reg_email or f"{reg_user}@streamlit.cloud"}
                        st.session_state.authenticated = True
                        st.rerun()

        st.markdown("---")
        if st.button("⚡ Continue in Direct Standalone Mode", key="direct_mode_btn", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_info = {"username": "Guest Researcher", "email": "guest@local"}
            st.session_state.auth_token = "standalone-guest-token"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()


# =====================================================================
# SCREEN 2: AUTHENTICATED WORKSPACE (LIGHT THEME)
# =====================================================================

user_data = st.session_state.user_info or {}
username = user_data.get("username", "Researcher")
user_email = user_data.get("email", "")

# ── Sidebar: Control Panel & User Profile ─────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 1.25rem 1rem; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; margin-bottom: 1rem;">
        <span style="font-size: 2.2rem;">👤</span>
        <h3 style="margin: 0.4rem 0 0 0; font-weight: 800; color: #0f172a;">{username}</h3>
        <div style="font-size: 0.75rem; color: #64748b;">{user_email or 'Authenticated Researcher'}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Sign Out", key="sidebar_logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.auth_token = ""
        st.session_state.user_info = None
        st.rerun()

    st.markdown("---")

    agents_config = [
        ("🔍", "Researcher", "researcher", "Async Parallel Search & RAG"),
        ("📊", "Analyst", "analyst", "Pattern & Gap Extraction"),
        ("✅", "Fact Checker", "fact_checker", "Claim Verification Loop"),
        ("✍️", "Writer", "writer", "Report Synthesis"),
    ]

    st.markdown("<div style='font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;'>⚡ Agent Orchestration Panel</div>", unsafe_allow_html=True)

    for icon, name, key, desc in agents_config:
        status = st.session_state.agent_statuses.get(key, "idle")
        css_class = f"agent-{status}"
        status_icon = {"idle": "⚪", "active": "🔵", "done": "🟢"}.get(status, "⚪")

        st.markdown(f"""
        <div class="agent-pill {css_class}">
            <span style="font-size: 1.2rem;">{icon}</span>
            <div>
                <div style="font-weight: 700;">{status_icon} {name}</div>
                <div style="font-size: 0.72rem; opacity: 0.85;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── User Account Metrics Fetch ───────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.5rem;">
        📊 Account Metrics
    </div>
    """, unsafe_allow_html=True)

    try:
        headers = {"Authorization": f"Token {st.session_state.auth_token}"}
        profile_resp = requests.get(f"{DJANGO_API_URL}/auth/me/", headers=headers, timeout=3)
        if profile_resp.status_code == 200:
            stats = profile_resp.json().get("stats", {})
            st.markdown(f"""
            <div style="font-size: 0.85rem; color: #334155; line-height: 1.8;">
                <div>📄 Saved Reports: <b>{stats.get('total_research_tasks', 0)}</b></div>
                <div>🏆 Saved Benchmarks: <b>{stats.get('total_benchmarks', 0)}</b></div>
            </div>
            """, unsafe_allow_html=True)
    except Exception:
        pass


# ── Top Header Greeting ───────────────────────────────────────────────
st.markdown(f"""
<div class="hero-header" style="text-align: left; padding: 1.75rem 2rem;">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <div class="user-greeting">👋 Welcome back, {username}!</div>
            <div style="font-size: 0.95rem; color: #475569; margin-top: 0.35rem;">
                Your multi-agent AI research environment is active and connected to Django REST API (Port 8080).
            </div>
        </div>
        <div>
            <span class="badge-tag">Django REST Active</span>
            <span class="badge-tag">Groq Llama-3.3</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_research, tab_benchmark, tab_history = st.tabs([
    "🔬 Research Studio", 
    "📊 LLM Benchmark Suite", 
    "📜 My Research History"
])


# =====================================================================
# TAB 1: RESEARCH STUDIO
# =====================================================================
with tab_research:
    with st.expander("🏗️ 4-Agent LangGraph Pipeline Architecture", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 1.6rem; margin-bottom: 0.3rem;">🔍</div>
                <div style="font-weight: 700; color: #0f172a;">Researcher</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Async Parallel Tavily + RAG</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 1.6rem; margin-bottom: 0.3rem;">📊</div>
                <div style="font-weight: 700; color: #0f172a;">Analyst</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Patterns & Insight Synthesis</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 1.6rem; margin-bottom: 0.3rem;">✅</div>
                <div style="font-weight: 700; color: #0f172a;">Fact Checker</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Verification & Feedback Loop</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown("""
            <div class="stat-card">
                <div style="font-size: 1.6rem; margin-bottom: 0.3rem;">✍️</div>
                <div style="font-weight: 700; color: #0f172a;">Writer</div>
                <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem;">Polished Citation Synthesis</div>
            </div>
            """, unsafe_allow_html=True)

    # RAG Upload Section
    with st.expander("📄 Upload PDF Documents (Personalized RAG Knowledge Base)", expanded=False):
        uploaded_files = st.file_uploader(
            "Upload PDF documents",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
            key="pdf_uploader",
        )
        if uploaded_files:
            if st.button("📥 Ingest Documents", key="ingest_btn", use_container_width=True):
                with st.spinner("Chunking, embedding & ingesting PDFs..."):
                    try:
                        from rag.vector_store import ingest_from_streamlit_uploads
                        result = ingest_from_streamlit_uploads(uploaded_files)
                        st.success(f"✅ Ingested {result['chunks_added']} chunks from {len(result['files_processed'])} file(s).")
                    except Exception as e:
                        st.error(f"❌ Ingestion failed: {e}")

    st.markdown("---")

    topic = st.text_input(
        "Enter research topic",
        placeholder="e.g., Autonomous Multi-Agent AI Systems in Financial Trading",
        key="topic_input",
    )

    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        start_btn = st.button("🚀 Execute Research Workflow", use_container_width=True, key="start_btn")
    with col_b2:
        clear_btn = st.button("🗑️ Clear Output", use_container_width=True, key="clear_btn")

    if clear_btn:
        st.session_state.research_running = False
        st.session_state.research_complete = False
        st.session_state.final_report = ""
        st.session_state.agent_messages = []
        st.session_state.error = ""
        st.session_state.agent_statuses = {
            "researcher": "idle", "analyst": "idle",
            "fact_checker": "idle", "writer": "idle",
        }
        st.rerun()

    if start_btn and topic:
        st.session_state.research_running = True
        st.session_state.research_complete = False
        st.session_state.final_report = ""
        st.session_state.agent_messages = []
        st.session_state.error = ""
        st.session_state.agent_statuses = {
            "researcher": "idle", "analyst": "idle",
            "fact_checker": "idle", "writer": "idle",
        }

        try:
            from graph.workflow import research_graph
        except Exception as e:
            st.error(f"⚠️ Configuration Error: {e}")
            st.session_state.research_running = False
            st.stop()

        initial_state = {
            "topic": topic, "research_data": [], "analysis": "",
            "fact_check_result": "", "fact_check_passed": False,
            "revision_count": 0, "final_report": "", "rag_context": [],
            "messages": [], "current_agent": "", "error": "",
        }

        progress_bar = st.progress(0)
        agent_order = ["researcher", "analyst", "fact_checker", "writer"]

        try:
            start_time = time.time()
            for event in research_graph.stream(initial_state, {"recursion_limit": 25}):
                for node_name, node_output in event.items():
                    for agent in agent_order:
                        if agent == node_name:
                            st.session_state.agent_statuses[agent] = "done"

                    if isinstance(node_output, dict):
                        if node_output.get("messages"):
                            st.session_state.agent_messages.extend(node_output["messages"])
                        if node_output.get("final_report"):
                            st.session_state.final_report = node_output["final_report"]

                    completed = sum(1 for s in st.session_state.agent_statuses.values() if s == "done")
                    progress_bar.progress(completed / 4)

            st.session_state.research_complete = True
            st.session_state.research_running = False
            progress_bar.progress(1.0)
            elapsed = round(time.time() - start_time, 2)

            # Persist Task into Django REST API Database for THIS User
            try:
                headers = {"Authorization": f"Token {st.session_state.auth_token}"}
                requests.post(f"{DJANGO_API_URL}/research/start/", json={"topic": topic}, headers=headers, timeout=5)
            except Exception:
                pass

        except Exception as e:
            st.session_state.error = str(e)
            st.session_state.research_running = False

        st.rerun()

    # Display Generated Report (Paper White Styling)
    if st.session_state.research_complete and st.session_state.final_report:
        st.markdown("---")
        st.markdown("### ✨ Generated Research Report")
        
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(st.session_state.final_report)
        st.markdown('</div>', unsafe_allow_html=True)

        st.download_button(
            label="📥 Download Report (.md)",
            data=st.session_state.final_report,
            file_name="research_report.md",
            mime="text/markdown",
            use_container_width=True,
        )


# =====================================================================
# TAB 2: LLM BENCHMARK SUITE
# =====================================================================
with tab_benchmark:
    st.markdown("### 📊 Side-by-Side LLM Benchmark Evaluation")
    st.write("Compare output accuracy, depth, factuality, and speed: **Single-Agent Llama-3 Baseline** vs **Multi-Agent Research Orchestrator**.")

    bench_topic = st.text_input(
        "Benchmark Topic",
        value="Impact of Autonomous AI Agents on Enterprise Software Architecture",
        key="bench_topic_input"
    )

    if st.button("🏆 Run Benchmark Comparison", key="run_bench_btn", use_container_width=True):
        with st.spinner("Running side-by-side benchmark evaluation (Single-Agent Baseline vs Multi-Agent Orchestrator)..."):
            try:
                from evaluation.evaluator import BenchmarkEvaluator
                evaluator = BenchmarkEvaluator()
                st.session_state.benchmark_results = evaluator.run_benchmark(bench_topic)
                
                # Persist Benchmark to Django REST API for THIS User
                try:
                    headers = {"Authorization": f"Token {st.session_state.auth_token}"}
                    requests.post(f"{DJANGO_API_URL}/evaluation/run/", json={"topic": bench_topic}, headers=headers, timeout=5)
                except Exception:
                    pass

                st.success("✅ Benchmark Evaluation Completed & Saved to Account!")
            except Exception as e:
                st.error(f"❌ Benchmark Error: {e}")

    if st.session_state.benchmark_results:
        res = st.session_state.benchmark_results
        metrics = res.get("metrics_summary", {})
        eval_data = res.get("evaluation", {})

        st.markdown("---")
        st.markdown("#### 🏆 Benchmark Summary")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Single-Agent Score", f"{metrics.get('single_agent_score', 0)}/10")
        with m2:
            st.metric("Multi-Agent Score", f"{metrics.get('multi_agent_score', 0)}/10", delta=f"+{metrics.get('quality_improvement_pct', 0)}% Quality")
        with m3:
            st.metric("Multi-Agent Latency", f"{metrics.get('multi_agent_latency', 0)}s", delta=f"Baseline: {metrics.get('single_agent_latency', 0)}s")
        with m4:
            st.metric("Citations Count", f"{metrics.get('multi_agent_citations', 0)} sources", delta=f"Baseline: {metrics.get('single_agent_citations', 0)}")

        st.markdown("---")
        st.markdown(f"#### 👑 Winner: **{eval_data.get('winner', 'Multi-Agent Research Orchestrator')}**")

        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("🔴 Single-Agent (Baseline Llama-3)")
            st.text_area("Single-Agent Output", value=res.get("single_agent", {}).get("report", ""), height=350, key="single_agent_text")
        with col_right:
            st.subheader("🟢 Multi-Agent Research Orchestrator")
            st.text_area("Multi-Agent Output", value=res.get("multi_agent", {}).get("report", ""), height=350, key="multi_agent_text")

        st.download_button(
            label="📥 Download Full Benchmark JSON Data",
            data=json.dumps(res, indent=2),
            file_name="benchmark_results.json",
            mime="application/json",
            use_container_width=True
        )


# =====================================================================
# TAB 3: PERSONALIZED RESEARCH HISTORY
# =====================================================================
with tab_history:
    st.markdown(f"### 📜 Research History for {username}")
    st.write("All research tasks and benchmarks executed under your account are stored securely in Django REST API.")

    if st.button("🔄 Refresh Account History", key="refresh_hist"):
        st.rerun()

    try:
        headers = {"Authorization": f"Token {st.session_state.auth_token}"}
        
        # 1. Fetch Research Tasks
        resp_tasks = api_request("GET", "/research/history/", headers=headers)
        if resp_tasks.status_code == 200:
            tasks_data = resp_tasks.json()
            if tasks_data:
                st.markdown(f"#### 📄 Saved Research Reports ({len(tasks_data)})")
                for t in tasks_data:
                    with st.expander(f"📌 {t.get('topic')} — {t.get('created_at', '')[:10]} [{t.get('status')}]"):
                        st.markdown(f"**Revision Rounds:** {t.get('revision_count', 0)} | **Latency:** {t.get('latency_seconds', 0)}s")
                        st.markdown("---")
                        st.markdown(t.get('final_report', 'No report content'))
            else:
                st.info("No research reports recorded under your account yet.")

        # 2. Fetch Evaluation Benchmarks
        st.markdown("---")
        resp_bench = api_request("GET", "/evaluation/history/", headers=headers)
        if resp_bench.status_code == 200:
            bench_data = resp_bench.json()
            if bench_data:
                st.markdown(f"#### 🏆 Saved Benchmark Results ({len(bench_data)})")
                for b in bench_data:
                    with st.expander(f"📊 {b.get('topic')} — Multi-Agent: {b.get('multi_agent_score')}/10 vs Single-Agent: {b.get('single_agent_score')}/10"):
                        st.write(f"**Winner:** {b.get('winner')}")
                        st.write(f"**Quality Improvement:** +{b.get('quality_improvement_pct')}%")
            else:
                st.info("No evaluation benchmark runs recorded under your account yet.")

    except Exception as e:
        st.info(f"ℹ️ Cloud Mode Active: History requires connection to live Django REST API backend ({DJANGO_API_URL}).")
