import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import time

st.set_page_config(
    page_title="Research Orchestrator",
    page_icon="📎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session State Initializations ────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "☀️ Light"
if "final_report" not in st.session_state:
    st.session_state.final_report = ""
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []
if "agent_statuses" not in st.session_state:
    st.session_state.agent_statuses = {
        "researcher": "idle",
        "analyst": "idle",
        "fact_checker": "idle",
        "writer": "idle",
    }
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "research_count" not in st.session_state:
    st.session_state.research_count = 0

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<h3 style='margin-top: 0.5rem;'>📎 Research Orchestrator</h3>", unsafe_allow_html=True)
    st.caption("Multi-agent research pipeline")

    selected_theme = st.selectbox(
        "🎨 Appearance",
        ["☀️ Light", "🌙 Dark", "🌲 Emerald Slate"],
        index=["☀️ Light", "🌙 Dark", "🌲 Emerald Slate"].index(st.session_state.theme),
        key="theme_selector",
    )
    st.session_state.theme = selected_theme

    st.markdown("---")

    st.markdown('<div class="sidebar-title">Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files and st.button("Ingest PDFs", use_container_width=True):
        with st.spinner("Processing..."):
            try:
                from rag.vector_store import ingest_from_streamlit_uploads
                result = ingest_from_streamlit_uploads(uploaded_files)
                st.success(f"{result['chunks_added']} chunks ingested")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")

    st.markdown('<div class="sidebar-title">Knowledge Base</div>', unsafe_allow_html=True)
    try:
        from rag.vector_store import get_collection_stats
        stats = get_collection_stats()
        c1, c2 = st.columns(2)
        c1.metric("Docs", stats.get("research_docs", 0))
        c2.metric("Memory", stats.get("past_research", 0))
    except Exception:
        st.caption("No data yet")

    st.markdown("---")

    if st.button("Clear Knowledge Base", use_container_width=True):
        try:
            from rag.vector_store import clear_collection
            clear_collection("research_docs")
            clear_collection("past_research")
            st.success("Cleared")
        except Exception as e:
            st.error(str(e))

    if st.button("Reset Session", use_container_width=True):
        st.session_state.final_report = ""
        st.session_state.agent_messages = []
        st.session_state.agent_statuses = {k: "idle" for k in st.session_state.agent_statuses}
        st.rerun()

# ── Dynamic Theme CSS ────────────────────────────────────────────────
if st.session_state.theme == "☀️ Light":
    css_vars = """
        --bg-app: #f8fafc;
        --bg-sidebar: #ffffff;
        --bg-card: #ffffff;
        --text-main: #0f172a;
        --text-sub: #64748b;
        --border-color: #e2e8f0;
        --accent-color: #2563eb;
        --btn-bg: #0f172a;
        --btn-hover: #1e293b;
        --btn-text: #ffffff;
        --step-bg: #ffffff;
        --step-border: #cbd5e1;
        --step-text: #475569;
        --active-bg: #dbeafe;
        --active-border: #2563eb;
        --active-text: #1d4ed8;
        --done-bg: #dcfce7;
        --done-border: #16a34a;
        --done-text: #15803d;
    """
elif st.session_state.theme == "🌙 Dark":
    css_vars = """
        --bg-app: #0f172a;
        --bg-sidebar: #1e293b;
        --bg-card: #1e293b;
        --text-main: #f8fafc;
        --text-sub: #94a3b8;
        --border-color: #334155;
        --accent-color: #38bdf8;
        --btn-bg: #38bdf8;
        --btn-hover: #0284c7;
        --btn-text: #0f172a;
        --step-bg: #1e293b;
        --step-border: #334155;
        --step-text: #94a3b8;
        --active-bg: #0369a1;
        --active-border: #38bdf8;
        --active-text: #ffffff;
        --done-bg: #14532d;
        --done-border: #22c55e;
        --done-text: #4ade80;
    """
else:  # 🌲 Emerald Slate
    css_vars = """
        --bg-app: #061817;
        --bg-sidebar: #0b2926;
        --bg-card: #0b2926;
        --text-main: #f0fdf4;
        --text-sub: #86efac;
        --border-color: #164e48;
        --accent-color: #10b981;
        --btn-bg: #10b981;
        --btn-hover: #059669;
        --btn-text: #061817;
        --step-bg: #0b2926;
        --step-border: #164e48;
        --step-text: #86efac;
        --active-bg: #064e3b;
        --active-border: #10b981;
        --active-text: #a7f3d0;
        --done-bg: #064e3b;
        --done-border: #34d399;
        --done-text: #6ee7b7;
    """

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {{
    {css_vars}
}}

html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}}

[data-testid="stAppViewContainer"] {{
    background: var(--bg-app) !important;
}}

[data-testid="stSidebar"] {{
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-color) !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}}

[data-testid="stSidebar"] * {{
    color: var(--text-main) !important;
}}

header[data-testid="stHeader"] {{
    background: transparent !important;
}}

h1, h2, h3, h4, h5, h6 {{
    color: var(--text-main) !important;
    font-weight: 700 !important;
}}

p, span, div, label {{
    color: var(--text-main);
}}

.block-container {{
    padding-top: 3.5rem !important;
    max-width: 1100px !important;
}}

.top-bar {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 6px;
}}

.top-bar h1 {{
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    color: var(--text-main) !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.2 !important;
}}

.subtitle {{
    color: var(--text-sub);
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}}

.pipe-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 1.2rem 0 1.5rem 0;
    flex-wrap: wrap;
}}

.pipe-step {{
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--step-text);
    background: var(--step-bg);
    border: 1px solid var(--step-border);
    border-radius: 6px;
    padding: 6px 14px;
}}

.pipe-step.active {{
    color: var(--active-text);
    border-color: var(--active-border);
    background: var(--active-bg);
}}

.pipe-step.done {{
    color: var(--done-text);
    border-color: var(--done-border);
    background: var(--done-bg);
}}

.pipe-arrow {{ color: var(--text-sub); font-size: 0.85rem; }}

.metric-row {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 1rem 0 1.5rem 0;
}}

.metric-box {{
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 16px 18px;
}}

.metric-box .val {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-main);
}}

.metric-box .lbl {{
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--text-sub);
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-top: 2px;
}}

.log-entry {{
    font-size: 0.84rem;
    color: var(--text-main);
    padding: 8px 12px;
    border-left: 3px solid var(--border-color);
    margin-bottom: 6px;
    background: var(--bg-card);
    border-radius: 0 6px 6px 0;
}}

.agent-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    margin-bottom: 6px;
}}

.agent-row .left {{
    display: flex;
    align-items: center;
    gap: 8px;
}}

.agent-row .name {{
    font-weight: 600;
    font-size: 0.88rem;
    color: var(--text-main);
}}

.agent-row .desc {{
    font-size: 0.75rem;
    color: var(--text-sub);
}}

.badge {{
    font-size: 0.7rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
}}

.badge-idle {{ background: var(--bg-app); color: var(--text-sub); border: 1px solid var(--border-color); }}
.badge-done {{ background: var(--done-bg); color: var(--done-text); border: 1px solid var(--done-border); }}
.badge-running {{ background: var(--active-bg); color: var(--active-text); border: 1px solid var(--active-border); }}

.empty-state {{
    text-align: center;
    padding: 60px 20px;
    color: var(--text-sub);
}}

.empty-state .icon {{ font-size: 2.5rem; margin-bottom: 12px; }}
.empty-state .title {{ font-size: 1rem; font-weight: 600; color: var(--text-main); margin-bottom: 4px; }}
.empty-state .desc {{ font-size: 0.85rem; color: var(--text-sub); }}

/* ── FIX: Selectbox Dropdown Box Styling across all themes ─────────── */
div[data-testid="stSelectbox"] > div > div {{
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border-color) !important;
}}

div[data-testid="stSelectbox"] * {{
    color: var(--text-main) !important;
}}

div[data-baseweb="popover"] *, div[data-baseweb="menu"] * {{
    background-color: var(--bg-card) !important;
    color: var(--text-main) !important;
}}

/* ── FIX: Streamlit Input Fields ───────────────────────────────────── */
.stTextInput > div > div > input {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    color: var(--text-main) !important;
    font-size: 0.95rem !important;
}}

/* ── FIX: Buttons High Contrast across all themes ─────────────────── */
.stButton > button, .stDownloadButton > button {{
    background-color: var(--btn-bg) !important;
    color: var(--btn-text) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s ease !important;
}}

.stButton > button:hover, .stDownloadButton > button:hover {{
    background-color: var(--btn-hover) !important;
    color: var(--btn-text) !important;
    opacity: 0.95;
}}

.stButton > button *, .stDownloadButton > button * {{
    color: var(--btn-text) !important;
}}

/* ── FIX: File Uploader Container & Dropzone Theme Matching ────────── */
div[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploader"] section,
section[data-testid="stFileUploadDropzone"] {{
    background-color: var(--bg-card) !important;
    border: 1px dashed var(--border-color) !important;
    border-radius: 8px !important;
}}

section[data-testid="stFileUploadDropzone"] * {{
    color: var(--text-main) !important;
}}

div[data-testid="stFileUploader"] small,
div[data-testid="stFileUploader"] span,
div[data-testid="stFileUploader"] p {{
    color: var(--text-sub) !important;
}}

div[data-testid="stFileUploader"] button {{
    background-color: var(--btn-bg) !important;
    color: var(--btn-text) !important;
    border-radius: 6px !important;
}}

.stExpander {{
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 8px !important;
}}

div[data-testid="stExpander"] details {{
    border: none !important;
}}

.sidebar-title {{
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-sub);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    margin-top: 16px;
}}
</style>
""", unsafe_allow_html=True)

# ── Main Content Header ──────────────────────────────────────────────

st.markdown("""
<div class="top-bar">
    <span style="font-size:1.5rem;">📎</span>
    <h1>Research Orchestrator</h1>
</div>
<div class="subtitle">Enter a topic below. Four agents will research, analyze, fact-check, and write a report.</div>
""", unsafe_allow_html=True)

# Pipeline steps
agents_info = [
    ("🔍", "Researcher", "Searches the web and local docs", "researcher"),
    ("📊", "Analyst", "Finds themes, gaps, contradictions", "analyst"),
    ("✓", "Fact Checker", "Verifies claims, triggers revisions", "fact_checker"),
    ("✏️", "Writer", "Writes the final report", "writer"),
]

status_map = st.session_state.agent_statuses

pipe_html = '<div class="pipe-row">'
for i, (icon, name, _, key) in enumerate(agents_info):
    s = status_map.get(key, "idle")
    cls = "done" if s == "done" else ("active" if s == "running" else "")
    pipe_html += f'<div class="pipe-step {cls}">{icon} {name}</div>'
    if i < len(agents_info) - 1:
        pipe_html += '<span class="pipe-arrow">→</span>'
pipe_html += '</div>'
# Defensive API Key check compatible with all environments and Streamlit Cloud
def _check_key(k_name):
    val = os.getenv(k_name, "")
    if not val:
        try:
            val = str(st.secrets.get(k_name, ""))
        except Exception:
            pass
    return val

if not _check_key("GROQ_API_KEY") or not _check_key("TAVILY_API_KEY"):
    st.warning("⚠️ **API Keys Missing!** Please add `GROQ_API_KEY` and `TAVILY_API_KEY` to your Streamlit Cloud **Dashboard → App Settings → Secrets**.")

# Input row
col_in, col_btn = st.columns([5, 1])
with col_in:
    topic = st.text_input(
        "Topic",
        placeholder="e.g. Impact of AI on drug discovery",
        label_visibility="collapsed",
    )
with col_btn:
    run_clicked = st.button("Run ▶", use_container_width=True, disabled=st.session_state.is_running)

# ── Run Pipeline ─────────────────────────────────────────────────────

if run_clicked and topic:
    st.session_state.is_running = True
    st.session_state.final_report = ""
    st.session_state.agent_messages = []
    st.session_state.agent_statuses = {k: "idle" for k in st.session_state.agent_statuses}

    initial_state = {
        "topic": topic,
        "research_data": [],
        "analysis": "",
        "fact_check_result": "",
        "fact_check_passed": False,
        "revision_count": 0,
        "final_report": "",
        "rag_context": [],
        "messages": [],
        "current_agent": "",
        "error": "",
    }

    with st.status("Running pipeline...", expanded=True) as status_box:
        try:
            from graph.workflow import research_graph

            agent_icons = {"researcher": "🔍", "analyst": "📊", "fact_checker": "✓", "writer": "✏️"}

            for event in research_graph.stream(initial_state, {"recursion_limit": 25}):
                for node_name, node_output in event.items():
                    if node_name == "__end__":
                        continue

                    st.session_state.agent_statuses[node_name] = "done"
                    messages = node_output.get("messages", [])
                    st.session_state.agent_messages.extend(messages)

                    icon = agent_icons.get(node_name, "⚙️")
                    label = node_name.replace("_", " ").title()
                    st.write(f"{icon} **{label}** — done")
                    for msg in messages:
                        st.caption(msg)

                    if node_output.get("final_report"):
                        st.session_state.final_report = node_output["final_report"]

            status_box.update(label="Pipeline complete", state="complete")
        except Exception as e:
            status_box.update(label=f"Error: {str(e)[:80]}", state="error")
            st.error(str(e))

    st.session_state.is_running = False
    st.session_state.research_count += 1
    st.rerun()

# ── Stats Row ────────────────────────────────────────────────────────

completed = sum(1 for v in st.session_state.agent_statuses.values() if v == "done")

st.markdown(f"""
<div class="metric-row">
    <div class="metric-box">
        <div class="val">{len(st.session_state.agent_messages)}</div>
        <div class="lbl">Messages</div>
    </div>
    <div class="metric-box">
        <div class="val">{completed}/4</div>
        <div class="lbl">Agents Done</div>
    </div>
    <div class="metric-box">
        <div class="val">{st.session_state.research_count}</div>
        <div class="lbl">Researches</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Report / Empty State ─────────────────────────────────────────────

if st.session_state.final_report:
    st.markdown("---")

    tab_report, tab_log, tab_agents = st.tabs(["Report", "Activity Log", "Agents"])

    with tab_report:
        st.markdown(st.session_state.final_report)
        st.markdown("---")
        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            st.download_button(
                "Download .md",
                data=st.session_state.final_report,
                file_name="report.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "Download .txt",
                data=st.session_state.final_report,
                file_name="report.txt",
                mime="text/plain",
                use_container_width=True,
            )

    with tab_log:
        if st.session_state.agent_messages:
            for msg in st.session_state.agent_messages:
                st.markdown(f'<div class="log-entry">{msg}</div>', unsafe_allow_html=True)
        else:
            st.caption("No activity yet.")

    with tab_agents:
        for icon, name, desc, key in agents_info:
            s = st.session_state.agent_statuses.get(key, "idle")
            badge_cls = f"badge-{s}"
            st.markdown(f"""
            <div class="agent-row">
                <div class="left">
                    <span style="font-size:1.2rem;">{icon}</span>
                    <div>
                        <div class="name">{name}</div>
                        <div class="desc">{desc}</div>
                    </div>
                </div>
                <span class="badge {badge_cls}">{s}</span>
            </div>
            """, unsafe_allow_html=True)

elif not st.session_state.is_running:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">📎</div>
        <div class="title">No research yet</div>
        <div class="desc">Type a topic and hit Run to start.</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("How does this work?"):
        st.markdown("""
**Four agents run in sequence:**

1. **Researcher** — generates search queries, searches Tavily, pulls context from uploaded PDFs via ChromaDB.
2. **Analyst** — reads all collected data, identifies key themes, contradictions, consensus, and gaps.
3. **Fact Checker** — verifies claims against sources. If it finds problems, it sends the pipeline back to the Researcher (up to 2 times).
4. **Writer** — produces a final Markdown report and saves the session into vector memory for future reference.

You can upload PDFs in the sidebar to give the agents more context.
        """)
