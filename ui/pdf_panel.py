import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from pypdf import PdfReader
import os

from utils.constants import PDF_PATH


# --------------------------------------------------
# Cached disk access
# --------------------------------------------------
# `mtime` is part of the cache key purely so that replacing the PDF on disk
# (e.g. re-running create_embedding.py against a new manual) invalidates the
# cache automatically, without needing a manual cache-clear.

@st.cache_data(show_spinner=False)
def _load_pdf_bytes(path: str, mtime: float) -> bytes:
    with open(path, "rb") as f:
        return f.read()


@st.cache_data(show_spinner=False)
def _get_page_count(path: str, mtime: float) -> int:
    return len(PdfReader(path).pages)


# --------------------------------------------------
# Toolbar
# --------------------------------------------------
def _render_toolbar(page, total_pages):

    nav_prev, nav_input, nav_next, nav_close = st.columns(
        [1, 2, 1, 1.6]
    )

    with nav_prev:
        if st.button(
            "◀",
            use_container_width=True,
            disabled=page <= 1,
        ):
            st.session_state.selected_page = page - 1
            st.rerun()

    with nav_input:
        # Keep the widget's own state in sync with `selected_page` in case
        # it changed elsewhere (e.g. a "Page X" source button in the chat),
        # then let its on_change callback be the one true writer back.
        if st.session_state.get("_pdf_nav_input") != page:
            st.session_state["_pdf_nav_input"] = page

        def _jump_to_page():
            st.session_state.selected_page = st.session_state["_pdf_nav_input"]

        st.number_input(
            "Page",
            min_value=1,
            max_value=total_pages,
            step=1,
            key="_pdf_nav_input",
            on_change=_jump_to_page,
            label_visibility="collapsed",
        )

    with nav_next:
        if st.button(
            "▶",
            use_container_width=True,
            disabled=page >= total_pages,
        ):
            st.session_state.selected_page = page + 1
            st.rerun()

    with nav_close:
        if st.button("❌ Close", use_container_width=True):
            st.session_state.viewer_open = False
            st.session_state.selected_page = None
            st.rerun()

    st.caption(f"Page **{page}** of **{total_pages}**")


# --------------------------------------------------
# Main
# --------------------------------------------------
def render_pdf_panel():

    st.subheader("📄 FANUC Manual")

    if not os.path.exists(PDF_PATH):
        st.error(f"PDF not found at `{PDF_PATH}`.")
        return

    try:
        mtime = os.path.getmtime(PDF_PATH)
        total_pages = _get_page_count(PDF_PATH, mtime)
    except Exception as e:
        st.error(f"Could not read PDF: {e}")
        return

    page = st.session_state.selected_page

    if page is None:
        st.info("Select a source page from the chat to preview it here.")
        if st.button("❌ Close Viewer", use_container_width=True):
            st.session_state.viewer_open = False
            st.rerun()
        return

    # Clamp in case a stale page number (e.g. from a previously loaded PDF)
    # is sitting in session state.
    page = max(1, min(page, total_pages))

    _render_toolbar(page, total_pages)
    st.divider()

    with st.spinner("Loading manual..."):
        pdf_bytes = _load_pdf_bytes(PDF_PATH, mtime)

    pdf_viewer(
        input=pdf_bytes,
        width="100%",
        height=900,
        zoom_level="auto",
        viewer_align="center",
        show_page_separator=True,
        pages_to_render=[
            max(1, page - 1),
            page,
            min(total_pages, page + 1),
        ],
        render_text=True,
        # `scroll_to_page` only takes effect when the component mounts, not
        # on prop updates. Without a page-dependent key, Streamlit reuses
        # the same component instance across reruns and the scroll never
        # fires after the first load. Keying on the page forces a fresh
        # mount every time the target page changes.
        key=f"pdf_viewer_page_{page}",
    )