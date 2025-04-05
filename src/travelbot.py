import os
import re
import argparse
import logging
from datetime import datetime
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_community.llms import HuggingFacePipeline
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- Configuration ---
MODEL_ID = os.getenv("MODEL_ID", "google/flan-t5-base")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "vectordb_retrain")
INDEX_NAME = os.getenv("INDEX_NAME", "travelbot_retrain")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
SAMPLE_QUESTIONS_FILE = os.path.join("context", "sample_questions.txt")

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Append User Questions to Sample Questions File ---
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

# --- Hybrid Response ---
def hybrid_response(query, llm, retriever):
    """Generate a response using the LLM and retriever."""
    try:
        qa_chain = RetrievalQA(llm=llm, retriever=retriever)
        return qa_chain.run(query)
    except Exception as e:
        logger.error(f"❌ Error generating response: {e}")
        return f"Error generating response: {e}"

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

# --- CLI ---
def run_cli(llm, retriever, mode):
    """Run the CLI for user interaction."""
    print("\u2708\ufe0f AF TravelBot is ready. Ask your JTR/DAFI questions.")
    print("[SECURITY NOTICE] Do not enter names, SSNs, DOBs, addresses, or OPSEC info.")
    while True:
        query = input("\n> ")
        if query.lower() in ["exit", "quit"]:
            break

        log_user_question(query, mode)

        if detect_pii_or_opsec(query):
            print("\u26a0\ufe0f Input may contain sensitive information. Please rephrase your question.")
            continue

        result = hybrid_response(query, llm, retriever)
        print("\nAnswer:\n", result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AF TravelBot CLI")
    parser.add_argument(
        "--mode",
        choices=["simple", "chunk", "context"],
        default="context",
        help="Choose the bot mode: simple (app.py), chunk (chunkbot.py), or context (retrieve_context.py)."
    )
    args = parser.parse_args()

    if args.mode == "simple":
        from simplebot import main as simple_bot
        simple_bot()
    elif args.mode == "chunk":
        from chunkbot import main as chunk_bot
        chunk_bot()
    elif args.mode == "context":
        llm, retriever = load_model_and_retriever()
        run_cli(llm, retriever, args.mode)