import streamlit as st

def get_layout():
    """
    Returns the chat and PDF containers 
    """

    if st.session_state.viewer_open:
        chat_container, pdf_container = st.columns([3, 2], gap="large")
    else:
        chat_container = st.container()
        pdf_container = None

    return chat_container , pdf_container