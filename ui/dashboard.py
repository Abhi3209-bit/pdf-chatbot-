import streamlit as st

from retriever import get_index_stats

from stats import (
    get_questions_today,
)

def render_dashboard():

    index_stats = get_index_stats()

    questions_today = get_questions_today()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📑 Pages", index_stats["pages"])

    with col2:
        st.metric("🧩 Chunks", index_stats["chunks"])

    with col3:
        st.metric("💬 Questions Today", questions_today)

    with col4:
        st.metric("🟢 Status", "Ready")
