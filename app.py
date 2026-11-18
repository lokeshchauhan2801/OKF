"""OKF demo: ask one question and compare the answer without OKF and with OKF.

Run from the repository root (with the venv activated):
    python app.py
"""
from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# `python app.py` -> restart this file through Streamlit, which serves the web page.
if __name__ == "__main__" and not st.runtime.exists():
    from streamlit.web import cli as streamlit_cli

    sys.argv = ["streamlit", "run", str(Path(__file__).resolve()), *sys.argv[1:]]
    sys.exit(streamlit_cli.main())

from assistant import (
    Answer,
    find_concepts,
    format_inr,
    get_answer,
    load_concepts,
    load_sample_orders,
    messages_with_okf,
    messages_without_okf,
    SCHEMA,
)

load_dotenv(Path(__file__).resolve().parent / ".env")

# Three questions, three kinds of answer: a ₹ total, a count and a list of orders.
SAMPLE_QUESTIONS = [
    "What was our revenue in fiscal year 2026?",
    "How many orders were placed in fiscal year 2026?",
    "Which delivered orders are not revenue yet?",
]

st.set_page_config(page_title="OKF Demo", page_icon="📚", layout="wide")
st.title("Same question: without OKF vs with OKF")
st.caption("Bundle: bundles/acme_retail  ·  Model: DeepSeek")

concepts = load_concepts()
orders = {row["order_id"]: row for row in load_sample_orders()}

with st.expander("Example data: 5 orders (stays on this machine, the AI never sees it)"):
    st.dataframe(list(orders.values()), hide_index=True)

with st.expander(f"What is in the OKF bundle? ({len(concepts)} files)"):
    for c in concepts:
        status = c.frontmatter.get("status", "")
        st.markdown(f"- **{c.title}** · {c.frontmatter.get('type')} · `{status}` · `{c.relative_path}`")

st.write("**Try a question:**")
buttons = st.columns(len(SAMPLE_QUESTIONS))
for col, sample in zip(buttons, SAMPLE_QUESTIONS):
    if col.button(sample, use_container_width=True):
        st.session_state.question = sample

question = st.text_input("Your question (or type your own)", key="question")
if not question:
    st.stop()


def show(answer: Answer) -> None:
    st.markdown(f"**{answer.summary}**")
    if answer.is_order_list:
        # "amount" -> ₹ total, "orders" -> the list of order ids; then every order marked ✅ or ❌
        if answer.kind == "amount":
            st.metric("Total (sum of net_amount)", format_inr(answer.total))
        else:
            ids = ", ".join(map(str, answer.counted_ids)) or "none"
            st.metric(f"Orders returned: {len(answer.counted_ids)}", ids)
        st.dataframe(
            [
                {
                    "order": o["order_id"],
                    "status": o["order_status"],
                    "delivered_on": o["delivered_on"],
                    "net_amount (₹)": o["net_amount"],
                    "returned by the query": "✅" if int(o["order_id"]) in answer.counted_ids else "❌",
                }
                for o in orders.values()
            ],
            hide_index=True,
        )
    elif len(answer.rows) == 1 and len(answer.rows[0]) == 1:
        # A single value, e.g. a count
        (label, value), = answer.rows[0].items()
        st.metric(label, value)
    else:
        st.dataframe(answer.rows, hide_index=True)
    for note in answer.notes:
        st.markdown(f"- {note}")
    with st.expander("SQL query the AI wrote"):
        st.code(answer.sql or "-- the AI did not write a query", language="sql")


matches = find_concepts(question, concepts)
left, right = st.columns(2)

with left:
    st.subheader("❌ Without OKF")
    st.caption("The AI sees only the table schema, no data.")
    with st.expander("What the AI received"):
        st.code(SCHEMA, language="text")
    left_slot = st.empty()

with right:
    st.subheader("✅ With OKF")
    st.caption("The AI sees the same schema and also reads the matching OKF files.")
    with st.expander("What the AI received"):
        st.code(SCHEMA, language="text")
        for i, c in enumerate(matches, start=1):
            st.markdown(f"**[C{i}] {c.title}** (`{c.relative_path}`)")
    right_slot = st.empty()
    if matches:
        st.caption("OKF files used: " + " · ".join(f"[C{i}] {c.relative_path}" for i, c in enumerate(matches, start=1)))

# Ask both questions at the same time; show each answer as soon as it arrives.
jobs = {"left": messages_without_okf(question)}
if matches:
    jobs["right"] = messages_with_okf(question, matches)
else:
    right_slot.warning("No matching OKF file. Try a word like revenue or order.")

slots = {"left": left_slot, "right": right_slot}
for side in jobs:
    slots[side].info("⏳ Asking DeepSeek...")

with ThreadPoolExecutor(max_workers=2) as pool:
    futures = {pool.submit(get_answer, messages): side for side, messages in jobs.items()}
    for future in as_completed(futures):
        side = futures[future]
        with slots[side].container():
            try:
                show(future.result())
            except (RuntimeError, ValueError) as exc:
                st.error(str(exc))
