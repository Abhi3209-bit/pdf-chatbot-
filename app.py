from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st

from langchain_google_genai import ChatGoogleGenerativeAI
from retriever import retrieve_documents

def load_css():
    with open("styles.css") as f:
        st.markdown(
           f"<style>{f.read()}</style>",
             unsafe_allow_html=True)
load_css()        

# -------------------------------
# Initialize Gemini
# -------------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
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
   st.caption("Hybrid (Vector + MB25)")

   st.write("Reranker")
   st.caption("BAAI/bge-reranker-base")

   st.write("LLM")
   st.caption("Gemini 2.5 Flash")


st.title("FANUC AI Assistant")
st.caption("Industrial CNC Knowledge Assistant")


#----------------------------------
# DASHBOARD
#----------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
   st.metric(
      label="📑Pages",
      value="766"
   )
with col2:
   st.metric(
      label="🧩Chunks",
      value="2133"
   )

with col3:
   st.metric(
      label="🤖LLM",
      value="Gemini"
    )   

with col4:
   st.metric(
      label="🟢Status",
      value="Ready"
   )
   

# -------------------------------
# Display Previous Messages
# -------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


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

      source_pages.add(
        doc.metadata["page"] + 1
    )
    prompt = f"""
    You are a helpful assistant.

Answer ONLY from the provided context.

If the answer is not present in the context, say:

'I couldn't find this information in the document.'

Context:
{context}

Question:
{query}
"""

    stream = llm.stream(prompt)

    with st.chat_message("assistant"):
        response = st.write_stream(stream)
        st.markdown("### 📄 Sources")

        for page in sorted(source_pages):

         st.markdown(f"- Page {page}")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )
    with st.expander("📄 Retrieved Chunks"):

      for i, doc in enumerate( documents, start=1):

        st.markdown(
            f"### Chunk {i} (Page {doc.metadata['page'] + 1})"
        )

        st.write(doc.page_content)

        st.divider()   