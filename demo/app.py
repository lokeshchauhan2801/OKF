from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from assistant import ask_deepseek, load_concepts, retrieve_concepts

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

st.set_page_config(page_title="OKF Knowledge Assistant", page_icon="📚")
st.title("OKF Knowledge Assistant")
st.caption("A compact demo: open knowledge bundle → relevant concepts → DeepSeek answer")

bundle_root = ROOT / "bundles"
bundle_names = sorted(
    path.name for path in bundle_root.iterdir() if path.is_dir()
) if bundle_root.is_dir() else []
if not bundle_names:
    st.error("No OKF bundles were found under the bundles/ directory.")
    st.stop()

with st.sidebar:
    st.header("Demo setup")
    selected_bundle = st.selectbox("Knowledge bundle", bundle_names, index=0)
    model_name = os.getenv("LLM_MODEL", "deepseek-chat")
    st.write(f"**Provider:** `{os.getenv('LLM_PROVIDER', 'deepseek')}`")
    st.write(f"**Model:** `{model_name}`")
    st.caption("The bundle is read locally. Retrieved excerpts are sent to DeepSeek.")
    if not os.getenv("DEEPSEEK_API_KEY"):
        st.warning("Add DEEPSEEK_API_KEY to .env to enable answers.")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

try:
    concepts = load_concepts(bundle_root / selected_bundle)
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.write(
    f"Loaded **{len(concepts)} concepts** from `{selected_bundle}`. "
    "Ask about a metric, policy, table, or computation."
)
with st.expander("What is in this bundle?"):
    for concept in concepts:
        st.markdown(
            f"- **{concept.title}** — {concept.frontmatter.get('type', 'Unknown')} "
            f"(`{concept.relative_path}`)"
        )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption("Sources: " + " · ".join(message["sources"]))

question = st.chat_input("Ask a question about this OKF bundle")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        matches = retrieve_concepts(question, concepts)
        if not matches:
            answer = (
                "I could not find a matching concept in this bundle. "
                "Try using a term from a concept title, such as revenue or policy."
            )
            st.markdown(answer)
            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": []}
            )
        else:
            with st.spinner("Reading the OKF concepts and asking DeepSeek..."):
                try:
                    answer = ask_deepseek(question, matches)
                except (RuntimeError, ValueError) as exc:
                    st.error(str(exc))
                    answer = None
            if answer is not None:
                sources = [
                    f"[C{index}] {concept.title} ({concept.relative_path})"
                    for index, concept in enumerate(matches, start=1)
                ]
                st.markdown(answer)
                st.caption("Sources: " + " · ".join(sources))
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
