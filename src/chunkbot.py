import os
import re
import logging
from datetime import datetime
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFacePipeline
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

MODEL_ID = os.getenv("MODEL_ID", "google/flan-t5-base")
DB_PATH = os.getenv("DB_PATH", "vectordb")
EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- Append User Questions to Sample Questions File ---
def log_user_question(question):
    SAMPLE_QUESTIONS_FILE = os.path.join("context", "sample_questions.txt")
    try:
        if os.path.exists(SAMPLE_QUESTIONS_FILE):
            with open(SAMPLE_QUESTIONS_FILE, "r", encoding="utf-8") as f:
                if question.strip() in f.read():
                    return
        with open(SAMPLE_QUESTIONS_FILE, "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Q: {question.strip()} (Asked on {timestamp})\n")
        logger.info(f"✅ Logged question: {question}")
    except Exception as e:
        logger.error(f"❌ Failed to log question: {e}")

# --- PII/OPSEC Detection ---
def detect_pii_or_opsec(text):
    patterns = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{10}\b",  # Phone number
        r"\b\d{2}/\d{2}/\d{4}\b",  # DOB
        r"\b[A-Z]{2,6}\d{4,6}\b",  # DoD ID or tail number
        r"\b(?:classified|secret|mission|OPSEC|coordinates|grid ref|location)\b",
        r"[A-Z][a-z]+\s[A-Z][a-z]+"  # Full names (still naive)
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

# --- Model and Pipeline Loader ---
def load_model_and_pipeline(model_id):
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    pipe = pipeline("text2text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256)
    return HuggingFacePipeline(pipeline=pipe)

# --- Retriever Loader ---
def load_retriever(db_path, embeddings_model):
    return FAISS.load_local(
        db_path,
        HuggingFaceEmbeddings(model_name=embeddings_model),
        index_name="travelbot",
        allow_dangerous_deserialization=True
    ).as_retriever(search_type="similarity", search_kwargs={"k": 3})

# --- Main Function ---
def main():
    llm = load_model_and_pipeline(MODEL_ID)
    retriever = load_retriever(DB_PATH, EMBEDDINGS_MODEL)
    query_history = []

    logger.info("✅ ChunkBot is ready. Ask your PCS/TDY travel questions.")
    print("🔐 [SECURITY NOTICE] Do not enter names, SSNs, DOBs, addresses, or OPSEC-sensitive information.")

    while True:
        try:
            query = input("\n> ")
            if query.lower() in ["exit", "quit"]:
                logger.info("Exiting ChunkBot. Goodbye!")
                break
            if query.lower() == "help":
                print("\n💡 Help:\nType your question to retrieve relevant chunks.\nCommands:\n  history - View your query history\n  exit/quit - Exit the bot")
                continue
            if query.lower() == "history":
                print("\n🔍 Query History:")
                for idx, past_query in enumerate(query_history, 1):
                    print(f"{idx}. {past_query}")
                continue

            query_history.append(query)
            log_user_question(query)

            if detect_pii_or_opsec(query):
                print("⚠️ Input may contain sensitive information. Please rephrase your question.")
                continue

            docs = retriever.get_relevant_documents(query)
            if not docs:
                print("⚠️ No relevant documents found. Please try rephrasing your question.")
                continue

            for i, doc in enumerate(docs, 1):
                print(f"\n📄 Source {i}: {doc.metadata.get('source', 'Unknown')}")
                print(doc.page_content.strip())
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            print("⚠️ An error occurred. Please try again.")

if __name__ == "__main__":
    main()