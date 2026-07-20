import streamlit as st


def initialize_session():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "viewer_open" not in st.session_state:
        st.session_state.viewer_open = False

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = None
    
    if "pdf_zoom" not in st.session_state:
        st.session_state.pdf_zoom = 1.0