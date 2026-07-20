import streamlit as st

from retriever import retrieve_documents
from stats import log_query
from utils.stream import stream_text

from services.prompt import build_prompt
from services.memory import rewrite_query


# ==========================================================
# DISPLAY SOURCE BUTTONS
# ==========================================================

def display_sources(source_pages, message_index):

    if not source_pages:
        return

    st.markdown("### 📄 Sources")

    for page in sorted(source_pages):

        if st.button(
            f"📄 Page {page}",
            key=f"page_{message_index}_{page}",
            use_container_width=True,
        ):

            st.session_state.selected_page = page
            st.session_state.viewer_open = True
            st.rerun()


# ==========================================================
# DISPLAY RETRIEVED CHUNKS
# ==========================================================

def display_chunks(documents):

    if not documents:
        return

    with st.expander("📄 Retrieved Chunks"):

        for i, doc in enumerate(documents, start=1):

            page = doc.metadata.get("page")

            if page is None:
                page_text = "Unknown"
            else:
                page_text = page + 1

            st.markdown(
                f"### Chunk {i} (Page {page_text})"
            )

            st.write(doc.page_content)

            st.divider()


# ==========================================================
# DISPLAY COMPLETE CHAT HISTORY
# ==========================================================

def display_chat_history():

    for index, message in enumerate(st.session_state.messages):

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            # Show sources for assistant messages
            if (
                message["role"] == "assistant"
                and "sources" in message
            ):

                display_sources(
                    message["sources"],
                    index,
                )

            # Show retrieved chunks
            if (
                message["role"] == "assistant"
                and "chunks" in message
            ):

                with st.expander("📄 Retrieved Chunks"):

                    for i, chunk in enumerate(message["chunks"], start=1):

                        page = chunk["page"]

                        if page is None:
                            page_text = "Unknown"
                        else:
                            page_text = page + 1

                        st.markdown(
                            f"### Chunk {i} (Page {page_text})"
                        )

                        st.write(chunk["text"])

                        st.divider()
# ==========================================================
# PROCESS USER QUERY
# ==========================================================

def process_query(llm, query):

    # -------------------------------
    # Display User Message
    # -------------------------------

    with st.chat_message("user"):
        st.markdown(query)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    log_query(query)

    # -------------------------------
    # Rewrite Query Using Memory
    # -------------------------------

    history = st.session_state.messages[-6:-1]

    rewritten_query = rewrite_query(
        llm,
        history,
        query,
    )

    # Uncomment while debugging
    # st.caption(f"🔍 Rewritten Query: {rewritten_query}")

    # -------------------------------
    # Retrieve Documents
    # -------------------------------

    documents = retrieve_documents(
        rewritten_query
    )

    context = ""

    source_pages = set()

    for doc in documents:

        context += doc.page_content + "\n\n"

        page = doc.metadata.get("page")

        if page is not None:
            source_pages.add(page + 1)

    # -------------------------------
    # Build Prompt
    # -------------------------------

    prompt = build_prompt(
        context,
        rewritten_query,
    )

    # -------------------------------
    # Generate Response
    # -------------------------------

    with st.chat_message("assistant"):

        response = st.write_stream(
            stream_text(
                llm.stream(prompt)
            )
        )

        display_sources(
            source_pages,
            len(st.session_state.messages)
        )

        display_chunks(
            documents
        )

    # -------------------------------
    # Save Assistant Message
    # -------------------------------
    chunks = []

    for doc in documents:

        chunks.append(
        {
            "page": doc.metadata.get("page"),
            "text": doc.page_content,
        }
    )




    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
            "sources": list(source_pages),
            "documents": documents,
            "rewritten_query": rewritten_query,
        }
    )


# ==========================================================
# MAIN CHAT
# ==========================================================

def render_chat(llm):

    # -------------------------------
    # Display Previous Conversation
    # -------------------------------

    display_chat_history()

    # -------------------------------
    # Chat Input
    # -------------------------------

    query = st.chat_input(
        "Ask your question..."
    )

    if not query:
        return

    # -------------------------------
    # Process Question
    # -------------------------------

    try:

        process_query(
            llm,
            query,
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"Something went wrong:\n\n{e}"
        )