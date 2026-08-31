import pandas as pd
import streamlit as st

from workspace_api import ApiError


api = st.session_state.api_client
token = st.session_state.get("auth_token", "")
st.caption("Your saved research runs are private to your account.")

try:
    result = api.list_jobs(token)
except ApiError as error:
    st.error(error.message, icon=":material/error:")
    st.stop()

jobs = result.get("jobs", [])
if not jobs:
    st.info("No saved research yet. Start a run from Research.", icon=":material/folder_open:")
    st.stop()

table = pd.DataFrame(jobs)[["id", "topic", "status", "web_sources_count", "revision_count", "created_at"]]
table.columns = ["ID", "Topic", "Status", "Web sources", "Revisions", "Created"]
st.dataframe(table, hide_index=True, width="stretch")

job_ids = [job["id"] for job in jobs]
selected_id = st.selectbox("Open a saved run", job_ids, format_func=lambda job_id: next(job["topic"] for job in jobs if job["id"] == job_id))
try:
    selected = api.get_job(token, selected_id)
except ApiError as error:
    st.error(error.message, icon=":material/error:")
    st.stop()

st.subheader(selected["topic"])
st.badge(selected["status"].title(), color={"completed": "green", "failed": "red", "running": "blue", "queued": "orange"}.get(selected["status"], "gray"))
if selected["final_report"]:
    st.markdown(selected["final_report"])
else:
    st.caption("This run has not produced a final report yet.")

if st.button("Delete this run", icon=":material/delete:", type="secondary"):
    try:
        api.delete_job(token, selected_id)
        if st.session_state.get("active_job_id") == selected_id:
            st.session_state.active_job_id = None
            st.session_state.active_job = None
        st.toast("Research run deleted", icon=":material/delete:")
        st.rerun()
    except ApiError as error:
        st.error(error.message, icon=":material/error:")
