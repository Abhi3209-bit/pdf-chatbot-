import streamlit as st
from stats import get_weekly_counts, get_recent_questions


def render_sidebar():

    with st.sidebar:

        st.title("FANUC AI")

        st.divider()

        st.success("Knowledge Base Loaded")

        st.write("FANUC Parameter Manual")

        st.divider()

        st.subheader("System Information")

        st.write("Embedding Model")
        st.caption("BAAI/bge-base-en-v1.5")

        st.write("Retriever")
        st.caption("Hybrid (Vector + BM25)")

        st.write("Reranker")
        st.caption("BAAI/bge-reranker-base")

        st.write("LLM")
        st.caption("Gemini 2.5 Flash")
        
        
        st.divider()

        with st.expander("📊 Usage This Week", expanded=False):

            weekly_counts = get_weekly_counts()

            st.bar_chart(weekly_counts)

            recent = get_recent_questions()

            if recent:

                st.markdown("**Recent Questions**")

                for item in recent:

                    st.markdown(
                        f"• {item['query']}  \n"
                        f"<small>{item['time_ago']}</small>",
                        unsafe_allow_html=True,
                    )

            else:

                st.caption("No questions asked yet.")