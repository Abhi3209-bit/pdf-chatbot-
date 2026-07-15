
import os
import streamlit as st

from langchain_google_genai import ChatGoogleGenerativeAI
from retriever import retrieve_documents

from dotenv import load_dotenv
load_dotenv()

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


st.set_page_config(
    page_title="FANUC AI Assistant",
    page_icon="🤖",
    layout="wide",
)
load_css()

# -------------------------------
# Initialize Gemini
# -------------------------------

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error(
        "Google API key not found. Please set the GOOGLE_API_KEY environment variable."
    )
    st.stop()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=api_key
)

# -------------------------------
# Chat History
# -------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# -------------------------------
# UI
# -------------------------------
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


st.title("FANUC AI Assistant")
st.caption("Industrial CNC Knowledge Assistant")


# ----------------------------------
# DASHBOARD
# ----------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="📑Pages", value="766")
with col2:
    st.metric(label="🧩Chunks", value="21572")
with col3:
    st.metric(label="🤖LLM", value="Gemini")
with col4:
    st.metric(label="🟢Status", value="Ready")


# -------------------------------
# Display Previous Messages
# -------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# -------------------------------
# Helper: turn LangChain stream into plain text chunks
# -------------------------------

def stream_text(stream):
    """LangChain's llm.stream() yields AIMessageChunk objects, not raw
    strings. st.write_stream needs plain strings, so unwrap .content here."""
    for chunk in stream:
        if chunk.content:
            yield chunk.content
                      
# -------------------------------
# User Input
# -------------------------------

query = st.chat_input("Ask your question...")

if query:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    # -------------------------------
    # Retrieve Relevant Chunks using MMR
    # -------------------------------

    documents = retrieve_documents(query)

    context = ""
    source_pages = set()

    for doc in documents:
        context += doc.page_content + "\n\n"
        source_pages.add(doc.metadata["page"] + 1)

    prompt = f"""You are a helpful assistant.

You are an AI assistant specialized in FANUC CNC manuals.

Use the provided context as the primary source of information.

If multiple retrieved chunks describe different parts of the same topic,
combine them into one complete and coherent explanation.

Do not simply repeat the retrieved text.
Summarize and organize the information into a clear answer.
- Combine information from multiple chunks when necessary.
- Do not infer or assume facts that are not explicitly stated

If some minor background explanation is needed to improve readability,
you may use your general engineering knowledge.
For parameter-related questions provide:

• Parameter Number
• Purpose
• Function
• Important Notes
• Related Parameters (if available)

However:

- Never invent FANUC parameter values.
- Never invent alarm codes.
- Never contradict the provided document.
- If the answer cannot be determined from the context,
state that it was not found in the manual.

Always explain in complete sentences rather than copying fragments.

Context:
{context}

Question:
{query}
"""
    try:
        stream = llm.stream(prompt)

        with st.chat_message("assistant"):
            response = st.write_stream(stream_text(stream))

            if source_pages:
                st.markdown("### 📄 Sources")
                for page in sorted(source_pages):
                    st.markdown(f"- Page {page}")

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        if documents:
            with st.expander("📄 Retrieved Chunks"):
                for i, doc in enumerate(documents, start=1):
                    st.markdown(f"### Chunk {i} (Page {doc.metadata['page'] + 1})")
                    st.write(doc.page_content)
                    st.divider()
    except Exception as e:
        st.error(f"Something went wrong while generating a response: {e}")
