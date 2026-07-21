from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from utils.constants import EMBEDDING_MODEL
from utils.constants import PDF_PATH
from utils.pdf_tables import extract_tables_from_pdf
import pickle


def create_vector_database():
    print("Loading PDF...")

    # Load text from each page
    loader = PyPDFLoader(PDF_PATH)
    text_docs = loader.load()

    print(f"Loaded {len(text_docs)} pages of text.")

    # Mark text documents so we can distinguish them from tables later
    for doc in text_docs:
        doc.metadata["content_type"] = "text"

    # Extract tables with pdfplumber
    print("Extracting tables with pdfplumber...")
    table_docs = extract_tables_from_pdf(PDF_PATH)
    print(f"Extracted {len(table_docs)} tables.")

    # Split only text — keep tables whole
    splitter = RecursiveCharacterTextSplitter(
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ],
        chunk_size=200,
        chunk_overlap=20,                           
    )
    text_chunks = splitter.split_documents(text_docs)

    # Do NOT split table chunks — splitting breaks row/column structure
    table_chunks = table_docs

    # Combine both into one index
    chunks = text_chunks + table_chunks

    # Save chunks for BM25
    with open("chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print(f"Created {len(text_chunks)} text chunks and {len(table_chunks)} table chunks.")
    print(f"Total chunks: {len(chunks)}")

    # Load the embedding model
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    print("Creating embeddings and saving to Chroma database...")

    # Create and persist the vector database
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    print("✅ Vector database created successfully!")

    return vector_db


if __name__ == "__main__":
    create_vector_database()
    
    
    
    
    
    
    
    