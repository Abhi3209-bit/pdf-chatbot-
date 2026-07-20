

from utils.css import load_css
from utils.session import initialize_session
from services.llm import load_llm
from ui.sidebar import render_sidebar
from ui.dashboard import render_dashboard
from utils.constants import APP_TITLE, APP_CAPTION
from ui.chat import render_chat
from ui.layout import get_layout
from ui.pdf_panel import render_pdf_panel
import streamlit as st


from dotenv import load_dotenv
load_dotenv()

st.set_page_config(
    page_title=(APP_TITLE),
    page_icon="🤖",
    layout="wide",
)
load_css()
initialize_session() 
llm = load_llm()
render_sidebar()


st.title(APP_TITLE)
st.caption(APP_CAPTION)

# -------------------------------
# Dynamic Layout
# -------------------------------

chat_container , pdf_container = get_layout()


# ----------------------------------
# DASHBOARD
# ----------------------------------
with chat_container:
    render_dashboard()
    render_chat(llm)


# -------------------------------
# PDF Viewer Panel
# -------------------------------

if pdf_container:

    with pdf_container:

        render_pdf_panel()