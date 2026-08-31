"""API-first Streamlit workspace for the Multi-Agent Research Orchestrator."""
from __future__ import annotations

import os

import streamlit as st

from workspace_api import ApiClient, ApiError


st.set_page_config(
    page_title="Research workspace",
    page_icon=":material/auto_awesome:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _api_base_url() -> str:
    configured = os.getenv("BACKEND_API_URL", "")
    if not configured:
        try:
            configured = str(st.secrets.get("BACKEND_API_URL", ""))
        except Exception:
            configured = ""
    return configured.rstrip("/") or "http://127.0.0.1:8000/api"


@st.cache_resource
def get_api_client(base_url: str) -> ApiClient:
    return ApiClient(base_url)


for key, default in {
    "auth_token": "",
    "auth_user": None,
    "active_job_id": None,
    "active_job": None,
}.items():
    st.session_state.setdefault(key, default)

api = get_api_client(_api_base_url())
st.session_state.api_client = api

with st.sidebar:
    st.markdown(":material/auto_awesome: **Research workspace**")
    st.caption("Multi-agent research with durable evidence and reports.")

    try:
        api.health()
        st.success("API connected", icon=":material/check_circle:")
    except ApiError:
        st.warning("API unavailable", icon=":material/cloud_off:")
        st.caption(f"Start Django at `{_api_base_url()}`")

    if st.session_state.auth_token:
        user = st.session_state.auth_user or {}
        st.subheader("Account")
        st.write(user.get("username", "Signed in"))
        if st.button("Sign out", icon=":material/logout:", width="stretch"):
            try:
                api.logout(st.session_state.auth_token)
            except ApiError:
                pass
            st.session_state.auth_token = ""
            st.session_state.auth_user = None
            st.session_state.active_job_id = None
            st.session_state.active_job = None
            st.rerun()
    else:
        st.subheader("Sign in to save work")
        login_tab, register_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            with st.form("login_form", border=False):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                login_submitted = st.form_submit_button("Sign in", icon=":material/login:", width="stretch")
            if login_submitted:
                try:
                    payload = api.login(username, password)
                    st.session_state.auth_token = payload["token"]
                    st.session_state.auth_user = payload["user"]
                    st.rerun()
                except ApiError as error:
                    st.error(error.message)
        with register_tab:
            with st.form("register_form", border=False):
                username = st.text_input("Username", key="register_username")
                email = st.text_input("Email", key="register_email")
                password = st.text_input("Password", type="password", key="register_password")
                register_submitted = st.form_submit_button("Create account", icon=":material/person_add:", width="stretch")
            if register_submitted:
                try:
                    payload = api.register(username, email, password)
                    st.session_state.auth_token = payload["token"]
                    st.session_state.auth_user = payload["user"]
                    st.rerun()
                except ApiError as error:
                    st.error(error.message)

pages = [
    st.Page("app_pages/research.py", title="Research", icon=":material/travel_explore:"),
]
if st.session_state.auth_token:
    pages.insert(1, st.Page("app_pages/library.py", title="Library", icon=":material/folder_open:"))
pages.append(st.Page("app_pages/benchmark.py", title="Benchmark", icon=":material/balance:"))

page = st.navigation(pages, position="top")
st.title(page.title)
page.run()
