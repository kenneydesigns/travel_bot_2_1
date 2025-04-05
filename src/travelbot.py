import os
import re
import argparse
import logging
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_community.llms import HuggingFacePipeline

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Configuration ---
MODEL_ID = "google/flan-t5-base"
USE_RETRAINED_INDEX = True
VECTOR_DB_PATH = "vectordb_retrain" if USE_RETRAINED_INDEX else "vectordb"
INDEX_NAME = "travelbot_retrain" if USE_RETRAINED_INDEX else "travelbot"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SOURCE_VERSION_MAP = {
    "jtr_mar2025_chunk0.txt": "JTR (March 2025)",
    "afman65-114_chunk0.txt": "AFMAN 65-114",
    "dafi36-3003_chunk0.txt": "DAFI 36-3003"
}

SAMPLE_QUESTIONS_FILE = "sample_questions.txt"  # Define the file path

def log_user_question(question, mode):
    """Log user questions to the sample_questions.txt file."""
    try:
        if os.path.exists(SAMPLE_QUESTIONS_FILE):
            with open(SAMPLE_QUESTIONS_FILE, "r", encoding="utf-8") as f:
                if question.strip() in f.read():
                    return

        with open(SAMPLE_QUESTIONS_FILE, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Q: {question.strip()} (Asked on {timestamp}, Mode: {mode})\n")
        logger.info(f"✅ Logged question: {question}")
    except Exception as e:
        logger.error(f"❌ Failed to log question: {e}")

def detect_pii_or_opsec(text):
    """Detect sensitive information in the input text."""
    safe_context_words = ["location", "airport", "TDY", "PCS", "JTR"]
    if any(word.lower() in text.lower() for word in safe_context_words):
        return False

def detect_pii_or_opsec(text):
    """Detect sensitive information in the input text."""
    safe_context_words = ["location", "airport", "TDY", "PCS", "JTR"]
    if any(word.lower() in text.lower() for word in safe_context_words):
        return False

    patterns = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{10}\b",  # 10-digit phone number
        r"\(\d{3}\)\s*\d{3}-\d{4}",  # (123) 456-7890
        r"\b\d{2}[-/]\d{2}[-/]\d{4}\b",  # DOB
        r"\b[A-Z]{2,6}\d{4,7}\b",  # DoD ID or tail number
        r"\b(classified|secret|OPSEC|grid ref|coordinates)\b"  # OPSEC terms
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False

# --- PII/OPSEC Detection ---
def detect_pii_or_opsec(text):
    """Detect sensitive information in the input text."""
    safe_context_words = ["location", "airport", "TDY", "PCS", "JTR"]
    if any(word.lower() in text.lower() for word in safe_context_words):
        return False

    patterns = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{10}\b",  # 10-digit phone number
        r"\(\d{3}\)\s*\d{3}-\d{4}",  # (123) 456-7890
        r"\b\d{2}[-/]\d{2}[-/]\d{4}\b",  # DOB
        r"\b[A-Z]{2,6}\d{4,7}\b",  # DoD ID or tail number
        r"\b(classified|secret|OPSEC|grid ref|coordinates)\b"  # OPSEC terms
    ]

    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    capitalized_words = re.findall(r"\b[A-Z][a-z]+\b", text)
    if len(capitalized_words) >= 2:
        for i in range(len(capitalized_words) - 1):
            pattern = f"{capitalized_words[i]} {capitalized_words[i+1]}"
            if re.search(rf"\b{re.escape(pattern)}\b", text):
                return True

    return False

# --- Model and Retriever Setup ---
def load_model_and_retriever():
    """Load the language model and FAISS retriever."""
    try:
        logger.info("📚 Loading language model...")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_ID)
        pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_new_tokens=100)
        llm = HuggingFacePipeline(pipeline=pipe)

        logger.info("🔍 Loading FAISS vector database...")
        db = FAISS.load_local(
            VECTOR_DB_PATH,
            HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL),
            index_name=INDEX_NAME,
            allow_dangerous_deserialization=True
        )
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        return llm, retriever
    except Exception as e:
        logger.error(f"Error loading model or retriever: {e}")
        raise

# --- Response Generation ---
def format_sources(retrieved):
    """Format the sources for display."""
    labels = set()
    for doc in retrieved:
        fname = doc.metadata["source"]
        label = SOURCE_VERSION_MAP.get(fname, fname.split("_chunk")[0])
        labels.add(label)
    return "\n".join(f"- {label}" for label in sorted(labels))

def hybrid_response(query, llm, retriever):
    """Generate a response to the user's query."""
    if detect_pii_or_opsec(query):
        return "\u26a0\ufe0f Input may contain sensitive information. Please rephrase your question."

    context_hint = (
        "Answer clearly and concisely using Air Force travel regulations when relevant. "
        "Use a helpful tone. Only include citations if needed."
    )
    pre_prompt = (
        f"The user asked: '{query}'. Please explain in a helpful and detailed way using regulation terms if possible."
    )
    full_prompt = context_hint + "\n\n" + pre_prompt
    preface = str(llm(full_prompt)).strip()

    retrieved = retriever.get_relevant_documents(query)
    raw_chunks = "\n\n".join(doc.page_content for doc in retrieved)

    if not retrieved or len(raw_chunks) < 200:
        return f"{preface}\n\nI couldn’t find a specific regulation that clearly answers this. You may want to consult your FSO or check JTR guidance for your PDS.\n\n---\nSources:\n{format_sources(retrieved)}"

    return f"{preface}\n\n---\n{raw_chunks}\n\n---\nSources:\n{format_sources(retrieved)}"

# --- CLI ---
def run_cli(llm, retriever):
    """Run the CLI for user interaction."""
    print("\u2708\ufe0f AF TravelBot is ready. Ask your JTR/DAFI questions.")
    print("[SECURITY NOTICE] Do not enter names, SSNs, DOBs, addresses, or OPSEC info.")
    while True:
        query = input("\n> ")
        if query.lower() in ["exit", "quit"]:
            break
        result = hybrid_response(query, llm, retriever)
        print("\nAnswer:\n", result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AF TravelBot CLI")
    parser.add_argument("--mode", choices=["friendly", "raw"], default="friendly", help="Choose response style.")
    args = parser.parse_args()

    llm, retriever = load_model_and_retriever()
    run_cli(llm, retriever)