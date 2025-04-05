import os
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import fitz  # PyMuPDF

# --- Configuration ---
SOURCE_DIR = "rag/source_docs"
CHUNK_DIR = "rag/jtr_chunks"
INDEX_DIR = "vectordb"
INDEX_NAME = "travelbot"
CHUNK_SIZE = 300
CHUNK_OVERLAP = 30
BAD_PHRASES = ["always entitled", "use LeaveWeb", "POV always reimbursed"]

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- PDF Text Extraction ---
def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        logger.info(f"📄 Extracting text from {pdf_path}...")
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text().strip() for page in doc)
    except Exception as e:
        logger.error(f"❌ Failed to extract text from {pdf_path}: {e}")
        return ""

# --- Chunk Splitting and Saving ---
def split_and_save_chunks(text, base_filename):
    """Split text into chunks and save them as .txt files."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    chunks = splitter.create_documents([text])
    saved_count = 0

    for i, chunk in enumerate(chunks):
        if len(chunk.page_content.strip()) > 100:  # Filter out nearly empty chunks
            if any(bad in chunk.page_content.lower() for bad in BAD_PHRASES):
                logger.warning(f"⚠️ Flagged chunk in {base_filename}_chunk{i} for manual review.")
                continue  # Skip saving this chunk

            first_line = chunk.page_content.split('\n')[0].strip()
            label = first_line if 0 < len(first_line) < 100 else "Unknown"

            chunk.metadata = {
                "source": f"{base_filename}_chunk{i}.txt",
                "chunk_index": i,
                "origin": base_filename,
                "label": label
            }

            try:
                chunk_path = os.path.join(CHUNK_DIR, f"{base_filename}_chunk{i}.txt")
                with open(chunk_path, "w", encoding="utf-8") as f:
                    f.write(chunk.page_content)
                saved_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to save chunk {base_filename}_chunk{i}: {e}")

    logger.info(f"✅ Saved {saved_count} valid chunks for {base_filename}")

# --- Rebuild Vector Database ---
def rebuild_vector_index():
    """Rebuild the FAISS vector database from chunks."""
    try:
        logger.info("🔄 Rebuilding FAISS vector database...")
        documents = []
        for fname in os.listdir(CHUNK_DIR):
            if fname.endswith(".txt"):
                with open(os.path.join(CHUNK_DIR, fname), "r", encoding="utf-8") as f:
                    documents.append(Document(page_content=f.read(), metadata={"source": fname}))

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        db = FAISS.from_documents(documents, embeddings)
        db.save_local(INDEX_DIR, index_name=INDEX_NAME)
        logger.info("✅ Vector DB updated and saved.")
    except Exception as e:
        logger.error(f"❌ Failed to rebuild vector database: {e}")

# --- Main Workflow ---
def clear_old_chunks():
    """Clear old chunks from the chunk directory."""
    logger.info("🧹 Clearing old chunks...")
    for file in os.listdir(CHUNK_DIR):
        try:
            os.remove(os.path.join(CHUNK_DIR, file))
        except Exception as e:
            logger.error(f"❌ Failed to delete {file}: {e}")

def process_pdfs():
    """Process all PDFs in the source directory."""
    for file in os.listdir(SOURCE_DIR):
        if file.endswith(".pdf"):
            logger.info(f"📄 Processing {file}...")
            full_text = extract_text_from_pdf(os.path.join(SOURCE_DIR, file))
            if full_text:
                base = os.path.splitext(file)[0]
                split_and_save_chunks(full_text, base)

def run():
    """Run the full workflow."""
    os.makedirs(CHUNK_DIR, exist_ok=True)
    os.makedirs(SOURCE_DIR, exist_ok=True)

    clear_old_chunks()
    process_pdfs()
    rebuild_vector_index()

if __name__ == "__main__":
    run()