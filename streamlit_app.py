"""Simple local interface for the Day 1 chat API and Day 2 workflow API."""

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="SuperBeing", page_icon="✨", layout="centered")
st.title("✨ SuperBeing")
chat_tab, workflow_tab = st.tabs(["Simple Chat", "Multi-Agent Workflow"])

with chat_tab:
    st.subheader("Simple Chat")
    st.caption("Day 1 single-provider chat")
    provider = st.selectbox("Provider", ["openai", "anthropic", "gemini"], key="chat_provider")
    prompt = st.text_area("Message", key="chat_message", height=120)
    if st.button("Send", key="chat_send") and prompt.strip():
        response = requests.post(f"{API_URL}/chat", json={"provider": provider, "prompt": prompt}, timeout=90)
        if response.ok:
            st.write(response.json()["content"])
        else:
            st.error(response.json().get("detail", "Chat request failed."))

with workflow_tab:
    st.subheader("Multi-Agent Workflow")
    st.caption("Planner → Executor → Verifier with transparent rule-based routing")
    display_provider = st.selectbox("Provider", ["Auto", "OpenAI", "Anthropic", "Gemini"], key="workflow_provider")
    message = st.text_area("Complex request", placeholder="Compare Java and Python for backend development.", key="workflow_message", height=140)
    if st.button("Run Workflow", type="primary") and message.strip():
        with st.spinner("Running sequential workflow..."):
            response = requests.post(f"{API_URL}/api/v1/workflow", json={"message": message, "provider": display_provider.lower()}, timeout=120)
        if not response.ok:
            st.error(response.json().get("detail", "Workflow request failed."))
        else:
            result = response.json()
            st.subheader("Final Answer")
            st.write(result["final_answer"])
            with st.expander("View Workflow Trace"):
                st.markdown("**Generated plan**")
                st.json(result["plan"])
                st.markdown("**Routing decisions**")
                for decision in result["routing_decisions"]:
                    st.write(f"{decision['task_type']} → **{decision['selected_provider']}** ({decision['model']}): {decision['reason']}")
                st.markdown("**Agent trace**")
                for entry in result["workflow_trace"]:
                    st.write(f"{entry['step']}. **{entry['agent']}** — {entry['status']} — {entry['provider']} ({entry['model']}): {entry['summary']}")
                    if entry.get("intermediate_draft"):
                        st.code(entry["intermediate_draft"], language=None)
