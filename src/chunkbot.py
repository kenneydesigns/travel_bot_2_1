import os
import re
import logging
import torch
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_community.llms import HuggingFacePipeline

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


from datetime import datetime

SAMPLE_QUESTIONS_FILE = os.path.join("context", "sample_questions.txt")

def log_user_question(question, mode="chunk"):
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
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

def load_model_and_pipeline(model_id):
    """Load the language model and pipeline."""
    try:
        logger.info(f"📚 Loading model: {model_id}")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        pipe = pipeline(
            "text2text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            repetition_penalty=1.2,
            top_k=50,
            top_p=0.95
        )
        llm = HuggingFacePipeline(pipeline=pipe)
        logger.info("✅ Model loaded successfully.")
        return llm
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def load_retriever(db_path, embeddings_model):
    """Load the FAISS retriever."""
    try:
        logger.info(f"🔍 Loading vector database from: {db_path}")
        retriever = FAISS.load_local(
            db_path,
            HuggingFaceEmbeddings(model_name=embeddings_model),
            index_name="travelbot",
            allow_dangerous_deserialization=True
        ).as_retriever(search_type="similarity", search_kwargs={"k": 3})
        logger.info("✅ Vector database loaded successfully.")
        return retriever
    except Exception as e:
        logger.error(f"Error loading vector database: {e}")
        raise

def main():
    """Main function to run the ChunkBot."""
    model_id = "google/flan-t5-base"
    db_path = "vectordb"
    embeddings_model = "sentence-transformers/all-MiniLM-L6-v2"

    # Load model and retriever
    llm = load_model_and_pipeline(model_id)
    retriever = load_retriever(db_path, embeddings_model)

    logger.info("✅ ChunkBot is ready. Ask your PCS/TDY travel questions.")
    print("🔐 [SECURITY NOTICE] Do not enter names, SSNs, DOBs, addresses, or OPSEC-sensitive information.")

    while True:
        try:
            query = input("\n> ")
            log_user_question(query, mode="chunk")
            if query.lower() in ["exit", "quit"]:
                logger.info("Exiting ChunkBot. Goodbye!")
                break

            if detect_pii_or_opsec(query):
                print("⚠️ Input may contain sensitive information. Please rephrase your question.")
                continue

            logger.info("🔍 Retrieving relevant chunk content...")
            docs = retriever.get_relevant_documents(query)

            if not docs:
                print("⚠️ No relevant documents found. Please try rephrasing your question.")
                continue

            for i, doc in enumerate(docs, 1):
                print(f"\n📄 Source {i}: {doc.metadata['source']}")
                print(doc.page_content.strip())
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            print("⚠️ An error occurred. Please try again.")

if __name__ == "__main__":
    main()