import pandas as pd
import streamlit as st

from workspace_api import ApiError


api = st.session_state.api_client
token = st.session_state.get("auth_token", "")
st.caption("Compare a single-agent baseline with the multi-agent pipeline on depth and verifiability.")

with st.form("benchmark_form"):
    topic = st.text_input("Benchmark topic", placeholder="Example: Best practices for RAG evaluation")
    run_submitted = st.form_submit_button("Run benchmark", type="primary", icon=":material/balance:")

if run_submitted:
    try:
        with st.status("Running benchmark", expanded=True) as status:
            st.write("Generating the single-agent baseline and multi-agent report.")
            benchmark = api.run_benchmark(token, topic)
            st.session_state.benchmark_result = benchmark
            status.update(label="Benchmark complete", state="complete")
    except ApiError as error:
        st.error(error.message, icon=":material/error:")

result = st.session_state.get("benchmark_result")
if result:
    metrics = result.get("evaluation_metrics", {})
    single = metrics.get("single_agent", {})
    multi = metrics.get("multi_agent", {})
    st.subheader("Latest benchmark")
    columns = st.columns(4)
    columns[0].metric("Single-agent depth", single.get("depth_score", 0))
    columns[1].metric("Multi-agent depth", multi.get("depth_score", 0))
    columns[2].metric("Single-agent verifiability", single.get("verifiability_score", 0))
    columns[3].metric("Multi-agent verifiability", multi.get("verifiability_score", 0))
    st.badge(metrics.get("verdict", "No verdict").replace("_", " "), color="blue")

    chart = pd.DataFrame(
        {
            "Single agent": [single.get("depth_score", 0), single.get("verifiability_score", 0)],
            "Multi-agent": [multi.get("depth_score", 0), multi.get("verifiability_score", 0)],
        },
        index=["Depth", "Verifiability"],
    )
    st.bar_chart(chart)

try:
    history = api.benchmark_history(token)
except ApiError:
    history = []

if history:
    st.subheader("Benchmark history")
    history_frame = pd.DataFrame(history)
    st.dataframe(history_frame, hide_index=True, width="stretch")
