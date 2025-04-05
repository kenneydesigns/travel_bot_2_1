import os
import torch

from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from langchain_huggingface.llms import HuggingFacePipeline
from transformers import PreTrainedTokenizerBase

model_id = "google/flan-t5-base"
print("🪶 Loading model: FLAN-T5 Base...")

def load_context_folder(path="context"):
    combined = ""
    for filename in sorted(os.listdir(path)):
        if filename.endswith(".txt"):
            with open(os.path.join(path, filename), "r") as f:
                combined += f.read().strip() + "\n\n"
    return combined.strip()

def trim_to_token_limit(text, tokenizer: PreTrainedTokenizerBase, max_tokens=400):
    tokens = tokenizer.encode(text, truncation=True, max_length=max_tokens)
    return tokenizer.decode(tokens, skip_special_tokens=True)

def trim_full_prompt(prompt, tokenizer: PreTrainedTokenizerBase, max_tokens=512):
    tokens = tokenizer.encode(prompt, truncation=True, max_length=max_tokens)
    return tokenizer.decode(tokens, skip_special_tokens=True)

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

db = FAISS.load_local(
    "vectordb",
    HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
    index_name="travelbot",
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

intro_context = load_context_folder("context")

if __name__ == "__main__":
    print("✈️ AF TravelBot is ready. Ask your JTR/DAFI questions.")
    while True:
        query = input("\n> ")
        if query.lower() in ["exit", "quit"]:
            break

        trimmed_intro = trim_to_token_limit(intro_context, tokenizer, max_tokens=250)
        raw_prompt = f"""{trimmed_intro}

User question: {query}
Answer:"""
        prompt = trim_full_prompt(raw_prompt, tokenizer, max_tokens=512)

        result = qa_chain.invoke(prompt)
        response = result["result"].strip()

        if response.lower() in ["yes", "no"]:
            response += "\n\n(Please verify details in the sources listed below. Travel entitlements may vary based on PCS type and location.)"

        print("\nAnswer:\n", response)
        print("\nSources:")
        for doc in result["source_documents"]:
            print(f"- {doc.metadata['source']}")
