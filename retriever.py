from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from sentence_transformers import CrossEncoder
import pickle
from rank_bm25 import BM25Okapi
import re
import streamlit as st


# Load embedding model only once
@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5"
    )


embeddings = load_embeddings()


# Load reranker model only once
@st.cache_resource
def load_reranker():
    return CrossEncoder(
        "BAAI/bge-reranker-base"
    )


reranker = load_reranker() 


# Connect to the existing Chroma database
@st.cache_resource
def load_vector_db():
    return Chroma(
        persist_directory="./chroma_db",
        embedding_function=embeddings
    )


vector_db = load_vector_db()


def tokenize(text):
    return re.findall(r"\b[\w./-]+\b", text.lower())


@st.cache_resource
def load_bm25():
    with open("chunks.pkl", "rb") as f:
        all_chunks = pickle.load(f)

    tokenized_docs = [
        tokenize(doc.page_content)
        for doc in all_chunks
    ]
    bm25 = BM25Okapi(tokenized_docs)
    return all_chunks, bm25


all_chunks, bm25 = load_bm25()


# Query patterns that suggest the user wants a specific parameter number
# (e.g. "parameter 3401", "No. 1815") rather than a general concept lookup.
PARAMETER_PATTERN = re.compile(r"\b(no\.?\s?\d+|\d{3,4})\b", re.IGNORECASE)


def retrieve_documents(query):
    """
    Retrieve relevant documents using a hybrid of vector search (similarity
    or MMR, depending on the query) and BM25, merged and reranked.
    """

    # --------------------------
    # Choose Retrieval Strategy
    # --------------------------

    if "parameter" in query.lower() or PARAMETER_PATTERN.search(query):
        search_type = "similarity"
        search_kwargs = {
            "k": 25
        }
    else:
        search_type = "mmr"
        search_kwargs = {
            "k": 25,
            "fetch_k": 60, 
            "lambda_mult": 0.7
        }
    retriever = vector_db.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs
    )

    # --------------------------
    # Chroma Retrieval
    # --------------------------

    vector_documents = retriever.invoke(query)

    # --------------------------
    # BM25 Retrieval
    # --------------------------

    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    top_indices = sorted(
      range(len(scores)),
        key=lambda i: scores[i],
     reverse=True
    )[:20]

    bm25_documents = [
        all_chunks[i]
        for i in top_indices
    ]

    # --------------------------
    # Merge + Deduplicate
    # --------------------------

    combined = {}

    for doc in vector_documents + bm25_documents:
        key = (
            doc.metadata.get("page"),
            hash(doc.page_content)
        )
        combined[key] = doc

    documents = list(combined.values())

    if not documents:
        return []

    # --------------------------
    # Rerank the merged documents
    # --------------------------

    pairs = [
        (query, doc.page_content)
        for doc in documents
    ]

    scores = reranker.predict(pairs)

    scored_docs = list(zip(scores, documents))

    scored_docs.sort(
        key=lambda x: x[0],
        reverse=True
    )

    top_documents = [
        doc
        for score, doc in scored_docs[:15]
    ]

    return top_documents

