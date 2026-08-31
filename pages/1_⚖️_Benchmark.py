"""
⚖️ Benchmark Lab — Streamlit page for the Multi-Agent Research Orchestrator.

Runs the single-agent vs multi-agent benchmark through the Django backend API
(`POST /api/research/benchmark/`) and charts historical `BenchmarkEvaluation`
results (`GET /api/benchmark/history/`).

Start the backend first:
    cd backend && python manage.py runserver
"""
import os
import sys

import pandas as pd
import requests
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Benchmark Lab",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── API base URL: env var → Streamlit secrets → default ──────────────
def _get_api_url() -> str:
    url = os.getenv("BACKEND_API_URL", "")
    if not url:
        try:
            url = str(st.secrets.get("BACKEND_API_URL", ""))
        except Exception:
            pass
    return url.rstrip("/") or "http://localhost:8000/api"


API_URL = _get_api_url()
BENCHMARK_URL = f"{API_URL}/research/benchmark/"
HISTORY_URL = f"{API_URL}/benchmark/history/"
HEALTH_URL = f"{API_URL}/health/"
LOGIN_URL = f"{API_URL}/auth/login/"
REGISTER_URL = f"{API_URL}/auth/register/"
PROFILE_URL = f"{API_URL}/auth/profile/"
LOGOUT_URL = f"{API_URL}/auth/logout/"
SESSIONS_URL = f"{API_URL}/research/sessions/"


# ── Auth helpers ─────────────────────────────────────────────────────
def _auth_headers() -> dict:
    """Return Authorization header if a token is stored in session state."""
    token = st.session_state.get("auth_token", "")
    if token:
        return {"Authorization": f"Token {token}"}
    return {}


def _api_post(url: str, payload: dict, timeout: int = 900) -> requests.Response:
    return requests.post(url, json=payload, headers=_auth_headers(), timeout=timeout)


def _api_get(url: str, timeout: int = 15) -> requests.Response:
    return requests.get(url, headers=_auth_headers(), timeout=timeout)


# ── Theme (shared with the main app via session_state) ───────────────
theme = st.session_state.get("theme", "☀️ Light")
if theme == "☀️ Light":
    css_vars = """
        --bg-app: #f8fafc; --bg-card: #ffffff; --text-main: #0f172a; --text-sub: #64748b;
        --border-color: #e2e8f0; --accent-color: #2563eb; --btn-bg: #0f172a; --btn-hover: #1e293b;
        --btn-text: #ffffff; --good: #15803d; --warn: #b45309; --bad: #b91c1c;
    """
elif theme == "🌙 Dark":
    css_vars = """
        --bg-app: #0f172a; --bg-card: #1e293b; --text-main: #f8fafc; --text-sub: #94a3b8;
        --border-color: #334155; --accent-color: #38bdf8; --btn-bg: #38bdf8; --btn-hover: #0284c7;
        --btn-text: #0f172a; --good: #4ade80; --warn: #fbbf24; --bad: #f87171;
    """
else:  # 🌲 Emerald Slate
    css_vars = """
        --bg-app: #061817; --bg-card: #0b2926; --text-main: #f0fdf4; --text-sub: #86efac;
        --border-color: #164e48; --accent-color: #10b981; --btn-bg: #10b981; --btn-hover: #059669;
        --btn-text: #061817; --good: #6ee7b7; --warn: #fcd34d; --bad: #fda4af;
    """

st.markdown(f"""
<style>
:root {{ {css_vars} }}
html, body, [data-testid="stAppViewContainer"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--bg-app) !important;
}}
[data-testid="stSidebar"] {{ background: var(--bg-app) !important; }}
h1, h2, h3 {{ color: var(--text-main) !important; }}
.block-container {{ padding-top: 3rem !important; max-width: 1100px !important; }}
.stButton > button {{
    background-color: var(--btn-bg) !important; color: var(--btn-text) !important;
    border: 1px solid var(--border-color) !important; border-radius: 8px !important;
    font-weight: 600 !important;
}}
.stButton > button:hover {{ background-color: var(--btn-hover) !important; }}
.stButton > button * {{ color: var(--btn-text) !important; }}
.stTextInput > div > div > input {{
    background: var(--bg-card) !important; border: 1px solid var(--border-color) !important;
    color: var(--text-main) !important; border-radius: 8px !important;
}}
.stExpander {{ background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom:4px;">
    <span style="font-size:1.5rem;">⚖️</span>
    <h1 style="font-size:1.6rem; margin:0;">Benchmark Lab</h1>
</div>
<div style="color:var(--text-sub); font-size:0.9rem; margin-bottom:1.2rem;">
    Single-agent baseline vs. the 4-agent pipeline — scored on depth &amp; verifiability.
</div>
""", unsafe_allow_html=True)

# ── Sidebar: Auth ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### 🔐 Authentication")

    if st.session_state.get("auth_token"):
        # Show logged-in state
        try:
            profile_resp = _api_get(PROFILE_URL, timeout=5)
            if profile_resp.ok:
                profile = profile_resp.json()
                st.success(f"**{profile['username']}**")
                st.caption(f"Researches: {profile.get('research_count', 0)}")
            else:
                st.success("Logged in")
        except Exception:
            st.success("Logged in")

        if st.button("Logout", use_container_width=True):
            try:
                _api_post(LOGOUT_URL, {}, timeout=5)
            except Exception:
                pass
            st.session_state.pop("auth_token", None)
            st.session_state.pop("auth_user", None)
            st.rerun()
    else:
        auth_tab_login, auth_tab_register = st.tabs(["Login", "Register"])

        with auth_tab_login:
            login_user = st.text_input("Username", key="login_username")
            login_pass = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True, key="login_btn"):
                if login_user and login_pass:
                    try:
                        resp = requests.post(
                            LOGIN_URL,
                            json={"username": login_user, "password": login_pass},
                            timeout=10,
                        )
                        if resp.ok:
                            data = resp.json()
                            st.session_state["auth_token"] = data["token"]
                            st.session_state["auth_user"] = data["user"]
                            st.success(f"Welcome, {data['user']['username']}!")
                            st.rerun()
                        else:
                            st.error(resp.json().get("error", "Login failed"))
                    except requests.RequestException as e:
                        st.error(f"Connection error: {e}")
                else:
                    st.warning("Please enter username and password")

        with auth_tab_register:
            reg_user = st.text_input("Username", key="reg_username")
            reg_email = st.text_input("Email (optional)", key="reg_email")
            reg_pass = st.text_input("Password", type="password", key="reg_password")
            if st.button("Register", use_container_width=True, key="reg_btn"):
                if reg_user and reg_pass:
                    try:
                        resp = requests.post(
                            REGISTER_URL,
                            json={"username": reg_user, "email": reg_email, "password": reg_pass},
                            timeout=10,
                        )
                        if resp.ok:
                            data = resp.json()
                            st.session_state["auth_token"] = data["token"]
                            st.session_state["auth_user"] = data["user"]
                            st.success(f"Account created! Welcome, {data['user']['username']}")
                            st.rerun()
                        else:
                            errors = resp.json()
                            error_msgs = []
                            for field, msgs in errors.items():
                                if isinstance(msgs, list):
                                    error_msgs.extend(msgs)
                                else:
                                    error_msgs.append(str(msgs))
                            st.error(" ".join(error_msgs))
                    except requests.RequestException as e:
                        st.error(f"Connection error: {e}")
                else:
                    st.warning("Please enter username and password")


# ── API helpers ──────────────────────────────────────────────────────


def check_health() -> tuple[bool, str]:
    try:
        r = requests.get(HEALTH_URL, timeout=10)
        if r.status_code == 200:
            return True, r.json().get("status", "online")
        return False, f"HTTP {r.status_code}"
    except requests.RequestException as e:
        return False, str(e)


def run_benchmark(topic: str) -> dict:
    r = _api_post(BENCHMARK_URL, {"topic": topic}, timeout=900)
    r.raise_for_status()
    return r.json()


def load_history() -> list[dict]:
    r = _api_get(HISTORY_URL, timeout=15)
    r.raise_for_status()
    return r.json()


def history_frame(records: list[dict]) -> pd.DataFrame:
    rows = []
    for item in records:
        rows.append({
            "Run": f"#{item['id']}",
            "created_at": item["created_at"],
            "topic": item["topic"],
            "single_agent_depth": item["single_agent_depth"],
            "multi_agent_depth": item["multi_agent_depth"],
            "single_agent_verifiability": item["single_agent_verifiability"],
            "multi_agent_verifiability": item["multi_agent_verifiability"],
            "verdict": item["verdict"],
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df = df.sort_values("created_at")
    return df


def verdict_badge(verdict: str) -> str:
    mapping = {
        "MULTI_AGENT_SUPERIOR": ("🟢 MULTI-AGENT SUPERIOR", "good"),
        "COMPARABLE": ("🟡 COMPARABLE", "warn"),
        "SINGLE_AGENT_SUPERIOR": ("🔴 SINGLE-AGENT SUPERIOR", "bad"),
    }
    label, color = mapping.get(verdict, (verdict, "warn"))
    return f'<span style="color:var(--{color}); font-weight:700;">{label}</span>'


# ── Connection status ────────────────────────────────────────────────
ok, detail = check_health()
if ok:
    st.success(f"✅ Backend API reachable at `{API_URL}` (status: {detail})")
else:
    st.warning(
        f"⚠️ Backend API not reachable at `{API_URL}` — {detail}. "
        "Start it with `cd backend && python manage.py runserver`."
    )

st.markdown("---")

# ── Run benchmark ────────────────────────────────────────────────────
st.markdown("### 🚀 Run a Benchmark")
col_in, col_btn = st.columns([5, 1])
with col_in:
    topic = st.text_input("Topic", placeholder="e.g. Best practices for RAG in 2026", label_visibility="collapsed")
with col_btn:
    run_clicked = st.button("Run Benchmark ▶", width="stretch", disabled=not ok)

if run_clicked and topic:
    with st.spinner("Benchmarking… single-agent baseline, 4-agent pipeline, and LLM judge. This takes 1–3 minutes."):
        try:
            result = run_benchmark(topic)
            st.session_state["benchmark_result"] = result
            st.session_state["benchmark_ran_at"] = pd.Timestamp.now()
        except requests.RequestException as e:
            st.error(f"Benchmark failed: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# ── Latest result ────────────────────────────────────────────────────
result = st.session_state.get("benchmark_result")
if result:
    metrics = result.get("evaluation_metrics", {})
    single = metrics.get("single_agent", {})
    multi = metrics.get("multi_agent", {})
    verdict = metrics.get("verdict", "")

    st.markdown("### 📊 Latest Result")
    st.markdown(f"**Topic:** {result.get('topic')}")

    cols = st.columns(5)
    cols[0].metric("Single Depth", single.get("depth_score", 0))
    cols[1].metric("Multi Depth", multi.get("depth_score", 0))
    cols[2].metric("Single Verifiability", single.get("verifiability_score", 0))
    cols[3].metric("Multi Verifiability", multi.get("verifiability_score", 0))
    cols[4].markdown(f"**Verdict**<br>{verdict_badge(verdict)}", unsafe_allow_html=True)

    # Side-by-side score comparison chart
    cmp = pd.DataFrame({
        "Metric": ["Depth", "Verifiability"],
        "Single-agent": [single.get("depth_score", 0), single.get("verifiability_score", 0)],
        "Multi-agent": [multi.get("depth_score", 0), multi.get("verifiability_score", 0)],
    }).set_index("Metric")
    st.bar_chart(cmp)

    with st.expander("📄 Single-agent baseline report"):
        baseline = result.get("single_agent_baseline", {})
        st.markdown(baseline.get("text", "_No report_"))
    with st.expander("📄 Multi-agent pipeline report"):
        st.markdown(result.get("multi_agent_report", "_No report_"))
    st.markdown("---")

# ── History ──────────────────────────────────────────────────────────
st.markdown("### 🕘 Historical Results")

if st.button("🔄 Refresh history"):
    st.session_state.pop("benchmark_history", None)

try:
    if "benchmark_history" not in st.session_state:
        with st.spinner("Loading history…"):
            st.session_state["benchmark_history"] = load_history()
    history = st.session_state["benchmark_history"]

    if not history:
        st.info("No benchmark evaluations yet. Run one above and it will appear here.")
    else:
        df = history_frame(history)
        st.caption(f"{len(df)} evaluation(s) — most recent first")

        # Table
        view = df[["Run", "created_at", "topic", "single_agent_depth", "multi_agent_depth",
                   "single_agent_verifiability", "multi_agent_verifiability", "verdict"]]
        view.columns = ["Run", "When", "Topic", "S Depth", "M Depth", "S Verif", "M Verif", "Verdict"]
        st.dataframe(view.iloc[::-1], width="stretch", hide_index=True)

        # Trend lines over time (index = created_at, one line per score)
        trend_cols = ["single_agent_depth", "multi_agent_depth",
                      "single_agent_verifiability", "multi_agent_verifiability"]
        if len(df) >= 2 and not df["created_at"].isna().all():
            st.markdown("**Scores over time**")
            st.line_chart(df.set_index("created_at")[trend_cols])

        # Grouped bars per run
        st.markdown("**Score comparison per run**")
        bar = df.set_index("Run")[trend_cols]
        st.bar_chart(bar)

        # Verdict distribution
        st.markdown("**Verdict distribution**")
        counts = df["verdict"].value_counts().reindex(
            ["MULTI_AGENT_SUPERIOR", "COMPARABLE", "SINGLE_AGENT_SUPERIOR"], fill_value=0)
        st.bar_chart(counts)

except requests.RequestException as e:
    st.error(f"Could not load history: {e}")
