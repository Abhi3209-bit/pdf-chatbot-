from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from utils.constants import EMBEDDING_MODEL
from utils.constants import PDF_PATH
import pickle


def create_vector_database():
    print("Loading PDF...")

    # Load the PDF
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()
    

    print(f"Loaded {len(docs)} pages.")

    # Split the document into chunks
    splitter = RecursiveCharacterTextSplitter(
    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ],
    chunk_size=100,
    chunk_overlap=20
 )
    chunks = splitter.split_documents(docs)
    # Save chunks for BM25
    with open("chunks.pkl", "wb") as f:
       pickle.dump(chunks, f)

    print(f"Created {len(chunks)} chunks.")

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
    
    
    
    
    
    
    
    
    