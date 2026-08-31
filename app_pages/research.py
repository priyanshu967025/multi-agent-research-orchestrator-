import pandas as pd
import streamlit as st

from workspace_api import ApiError


api = st.session_state.api_client
token = st.session_state.get("auth_token", "")
st.caption("Submit a topic, follow each agent stage, and keep the final evidence-backed report in your library.")

if not token:
    st.info("Sign in from the sidebar to create a durable research run.", icon=":material/login:")
    st.stop()

with st.form("research_form"):
    topic = st.text_area(
        "Research topic",
        placeholder="Example: What evidence supports using retrieval-augmented generation for internal knowledge assistants?",
        max_chars=512,
        height=120,
    )
    submitted = st.form_submit_button("Start research", type="primary", icon=":material/play_arrow:")

if submitted:
    try:
        job = api.create_job(token, topic)
        st.session_state.active_job_id = job["id"]
        st.session_state.active_job = job
        st.toast("Research job created", icon=":material/check_circle:")
        st.rerun()
    except ApiError as error:
        st.error(error.message, icon=":material/error:")

with st.expander("Add PDF context", icon=":material/upload_file:"):
    st.caption("Upload up to five PDFs, 10 MB each. Their text is added to the local research knowledge base.")
    with st.form("document_upload_form", border=False):
        documents = st.file_uploader(
            "PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            key="research_documents",
        )
        upload_submitted = st.form_submit_button("Add to knowledge base", icon=":material/upload:")
    if upload_submitted:
        if not documents:
            st.warning("Select at least one PDF.")
        else:
            try:
                uploaded = api.upload_documents(token, documents)
                st.success(f"Added {uploaded['chunks_added']} chunks from {len(uploaded['files_processed'])} document(s).")
            except ApiError as error:
                st.error(error.message, icon=":material/error:")

active_job_id = st.session_state.get("active_job_id")
if active_job_id:
    st.subheader("Research run")

    @st.fragment(run_every="4s")
    def live_job() -> None:
        try:
            job = api.get_job(token, active_job_id)
            st.session_state.active_job = job
        except ApiError as error:
            st.error(error.message, icon=":material/error:")
            return

        status = job["status"]
        status_colors = {"queued": "orange", "running": "blue", "completed": "green", "failed": "red"}
        st.badge(status.replace("_", " ").title(), color=status_colors.get(status, "gray"))
        st.caption(f"Topic: {job['topic']}")
        metrics = st.columns(3)
        metrics[0].metric("Evidence sources", job["web_sources_count"] + job["rag_chunks_count"])
        metrics[1].metric("Revision loops", job["revision_count"])
        metrics[2].metric("Elapsed", f"{job['duration_seconds'] or 0:.1f}s")

        events = job.get("events", [])
        if events:
            event_frame = pd.DataFrame(events)[["sequence", "stage", "message", "created_at"]]
            event_frame.columns = ["#", "Stage", "Activity", "Time"]
            st.dataframe(event_frame, hide_index=True, width="stretch")

        if status == "failed":
            st.error(job.get("error_message") or "Research could not be completed.", icon=":material/error:")
            return
        if status != "completed":
            st.info("This view refreshes automatically while the agents work.", icon=":material/autorenew:")
            return

        st.subheader("Report")
        st.markdown(job.get("final_report") or "No report content was returned.")

        report = job.get("final_report", "")
        downloads = st.container(horizontal=True)
        with downloads:
            st.download_button("Download Markdown", report, file_name=f"research-{job['id']}.md", mime="text/markdown", icon=":material/download:")
            st.download_button("Download text", report, file_name=f"research-{job['id']}.txt", mime="text/plain", icon=":material/download:")

        tags = job.get("tags", [])
        tag_str = ", ".join(t["name"] for t in tags) if tags else ""
        new_tag = st.text_input("Add a tag", value="", placeholder="e.g. machine-learning", key="tag_input")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Add tag", icon=":material/label:", disabled=not new_tag):
                try:
                    api.add_tag(token, job["id"], new_tag)
                    st.rerun()
                except ApiError as error:
                    st.error(error.message)
        if tag_str:
            st.caption(f"Tags: {tag_str}")

        with st.expander("Verification details", icon=":material/fact_check:"):
            st.markdown(job.get("fact_check_result") or "No fact-check detail was returned.")
        with st.expander("Evidence", icon=":material/source:"):
            for source in job.get("sources", []):
                with st.container(border=True):
                    st.caption(f"{source['source_type'].upper()} · {source.get('domain') or source.get('title')}")
                    if source.get("url"):
                        st.link_button("Open source", source["url"], icon=":material/open_in_new:")
                    st.write(source["snippet"])

    live_job()
else:
    with st.container(border=True):
        st.subheader("Autonomous Multi-Agent Architecture")
        st.write("Specialized AI agents collaborate to formulate multi-angle search queries, cross-examine evidence, verify claims against sources, and produce publication-ready Markdown reports with citations.")
        
        st.markdown("""
```mermaid
graph LR
    R["🔍 Researcher<br/><small>Web Search + RAG</small>"] --> A["📊 Analyst<br/><small>Themes & Gaps</small>"]
    A --> FC{"🛡️ Fact Checker<br/><small>Claim Verification</small>"}
    FC -- "Needs Revision (Gaps/Contradictions)" --> R
    FC -- "Verified (Pass)" --> W["✍️ Writer<br/><small>Cited Report + Memory</small>"]
    W --> END((🏁 Publication Report))
    
    style R fill:#2e1065,stroke:#a855f7,stroke-width:2px,color:#fff
    style A fill:#0c4a6e,stroke:#38bdf8,stroke-width:2px,color:#fff
    style FC fill:#713f12,stroke:#fbbf24,stroke-width:2px,color:#fff
    style W fill:#064e3b,stroke:#34d399,stroke-width:2px,color:#fff
    style END fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#fff
```
        """)
