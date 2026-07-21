import streamlit as st
from services.entity_memory import initialize_entity_memory

def initialize_session():

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "viewer_open" not in st.session_state:
        st.session_state.viewer_open = False

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = None
    
    if "pdf_zoom" not in st.session_state:
        st.session_state.pdf_zoom = 1.0
        
        initialize_entity_memory()