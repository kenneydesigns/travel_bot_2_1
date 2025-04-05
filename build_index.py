import os
import logging
import argparse
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration ---
CHUNK_DIR = "rag/jtr_chunks"
VECTOR_DB_DIR = "vectordb"
RETRAIN_DB_DIR = "vectordb_retrain"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# --- Build Index ---
def build_index(mode, flagged_files=None):
    """Build the FAISS vector database."""
    docs = []

    if mode == "all":
        logger.info("📂 Processing all chunks...")
        for filename in os.listdir(CHUNK_DIR):
            if filename.endswith(".txt"):
                with open(os.path.join(CHUNK_DIR, filename), "r", encoding="utf-8") as f:
                    text = f.read()
                    docs.append(Document(page_content=text, metadata={"source": filename}))
    elif mode == "retrain":
        logger.info("📂 Processing flagged chunks...")
        for fname in flagged_files:
            try:
                with open(os.path.join(CHUNK_DIR, fname), "r", encoding="utf-8") as f:
                    text = f.read()
                    docs.append(Document(page_content=text, metadata={"source": fname}))
            except FileNotFoundError:
                logger.warning(f"⚠️ File not found: {fname}")

    if not docs:
        logger.error("❌ No documents found to process.")
        return

    # Split documents into chunks
    splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.split_documents(docs)

    # Embed and save
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    db = FAISS.from_documents(chunks, embeddings)

    output_dir = RETRAIN_DB_DIR if mode == "retrain" else VECTOR_DB_DIR
    db.save_local(output_dir, index_name="travelbot" if mode == "all" else "travelbot_retrain")
    logger.info(f"✅ Vector database saved to {output_dir}")

# --- Main ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build or retrain the FAISS vector database.")
    parser.add_argument("--mode", choices=["all", "retrain"], required=True, help="Mode: all or retrain")
    parser.add_argument("--flagged_files", nargs="*", help="List of flagged files (required for retrain mode)")
    args = parser.parse_args()

    if args.mode == "retrain" and not args.flagged_files:
        parser.error("--flagged_files is required for retrain mode")

    build_index(args.mode, flagged_files=args.flagged_files)