import os
import logging
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# --- Configuration ---
USE_OLLAMA = False  # Must match app.py
DATA_DIR = "data"
VECTOR_DB_PATH = "vectordb"
INDEX_NAME = "travelbot"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 200

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def load_documents(data_dir):
    """Load documents from the specified directory."""
    docs = []
    if not os.path.exists(data_dir):
        logger.error(f"Data directory '{data_dir}' does not exist.")
        return docs

    for file in os.listdir(data_dir):
        if file.endswith(".pdf"):
            try:
                logger.info(f"📄 Loading file: {file}")
                loader = PyPDFLoader(os.path.join(data_dir, file))
                docs.extend(loader.load())
            except Exception as e:
                logger.error(f"Error loading file '{file}': {e}")
    if not docs:
        logger.warning("No documents found in the data directory.")
    return docs

def split_documents(docs, chunk_size, chunk_overlap):
    """Split documents into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)
    logger.info(f"✅ Split {len(docs)} documents into {len(chunks)} chunks.")
    return chunks

def create_embeddings(use_ollama):
    """Create the embedding engine."""
    if use_ollama:
        logger.info("🔧 Using Ollama embeddings.")
        return OllamaEmbeddings(model="tinyllama")
    else:
        logger.info("🔧 Using HuggingFace embeddings.")
        return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def save_to_faiss(chunks, embeddings, vector_db_path, index_name):
    """Save document chunks to a FAISS vector database."""
    try:
        logger.info("💾 Saving chunks to FAISS vector database...")
        db = FAISS.from_documents(chunks, embedding=embeddings)
        db.save_local(vector_db_path, index_name=index_name)
        logger.info(f"✅ Vector store saved to '{vector_db_path}/'")
    except Exception as e:
        logger.error(f"Error saving to FAISS vector database: {e}")

def main():
    """Main function to execute the ingestion process."""
    logger.info("🚀 Starting document ingestion...")

    # Load documents
    docs = load_documents(DATA_DIR)
    if not docs:
        logger.error("No documents to process. Exiting.")
        return

    # Split documents into chunks
    chunks = split_documents(docs, CHUNK_SIZE, CHUNK_OVERLAP)

    # Create embeddings
    embeddings = create_embeddings(USE_OLLAMA)

    # Save chunks to FAISS vector database
    save_to_faiss(chunks, embeddings, VECTOR_DB_PATH, INDEX_NAME)

    logger.info("✅ Ingestion process complete.")

if __name__ == "__main__":
    main()