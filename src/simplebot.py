import os
import re
import logging
from typing import Optional
import torch

from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_huggingface.llms import HuggingFacePipeline
from transformers import PreTrainedTokenizerBase

# --- Configuration ---
MODEL_ID = "google/flan-t5-base"
VECTOR_DB_PATH = "vectordb"
CONTEXT_FOLDER = "context"
MAX_TOKENS_PROMPT = 512
MAX_TOKENS_CONTEXT = 250

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- PII/OPSEC Detection ---
def detect_pii_or_opsec(text: str) -> bool:
    safe_words = ["dependents", "entitlements", "PCS", "TDY", "JTR", "DAFI"]
    if any(word.lower() in text.lower() for word in safe_words):
        return False

    patterns = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{10}\b",  # Phone number
        r"\b\d{2}/\d{2}/\d{4}\b",  # DOB
        r"\b[A-Z]{2,6}\d{4,6}\b",  # DoD ID or tail number
        r"\b(?:classified|secret|mission|OPSEC|coordinates|grid ref|location)\b",
        r"[A-Z][a-z]+\s[A-Z][a-z]+"  # Full names (still naive)
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)

def sanitize_input(text: str) -> str:
    if detect_pii_or_opsec(text):
        return "\u26a0\ufe0f Input may contain sensitive information. Please rephrase your question."
    return text

# --- Model Setup ---
def setup_model(model_id: str):
    logger.info(f"Loading model: {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id, device_map="auto")
    pipe = pipeline(
        "text2text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=128,
        do_sample=True,
        temperature=0.7,
        repetition_penalty=1.2,
        top_k=50,
        top_p=0.95
    )
    llm = HuggingFacePipeline(pipeline=pipe)
    return tokenizer, llm

# --- Vector DB Setup ---
def setup_vector_db(db_path: str):
    logger.info(f"Loading vector database from: {db_path}...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    db = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
    return db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# --- Helper Functions ---
def load_context_folder(path: str) -> str:
    combined = ""
    try:
        for filename in sorted(os.listdir(path)):
            if filename.endswith(".txt"):
                with open(os.path.join(path, filename), "r") as f:
                    combined += f.read().strip() + "\n\n"
    except Exception as e:
        logger.error(f"Error loading context folder: {e}")
    return combined.strip()

def trim_to_token_limit(text: str, tokenizer: PreTrainedTokenizerBase, max_tokens: int) -> str:
    tokens = tokenizer.encode(text, truncation=True, max_length=max_tokens)
    return tokenizer.decode(tokens, skip_special_tokens=True)

# --- Main Function ---
def main():
    tokenizer, llm = setup_model(MODEL_ID)
    retriever = setup_vector_db(VECTOR_DB_PATH)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever, return_source_documents=True)

    intro_context = load_context_folder(CONTEXT_FOLDER)
    trimmed_intro = trim_to_token_limit(intro_context, tokenizer, max_tokens=MAX_TOKENS_CONTEXT)

    print("\u2708\ufe0f AF TravelBot is ready. Ask your JTR/DAFI questions.")
    print("[SECURITY NOTICE] Do not enter names, SSNs, DOBs, addresses, or OPSEC info.")

    while True:
        try:
            query = input("\n> ")
            if query.lower() in ["exit", "quit"]:
                break

            query = sanitize_input(query)
            if query.startswith("\u26a0\ufe0f"):
                print(query)
                continue

            raw_prompt = f"""{trimmed_intro}

User question: {query}
Answer:"""
            prompt = trim_to_token_limit(raw_prompt, tokenizer, max_tokens=MAX_TOKENS_PROMPT)

            result = qa_chain.invoke(prompt)
            response = result["result"].strip()

            print("\nAnswer:\n", response)
            print("\nSources:")
            for doc in result["source_documents"]:
                print(f"- {doc.metadata['source']}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()