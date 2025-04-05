import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.ollama import OllamaEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

USE_OLLAMA = False  # Must match app.py

data_dir = "data"
docs = []

for file in os.listdir(data_dir):
    if file.endswith(".pdf"):
        loader = PyPDFLoader(os.path.join(data_dir, file))
        docs.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200)
chunks = splitter.split_documents(docs)

# Choose embedding engine
if USE_OLLAMA:
    embeddings = OllamaEmbeddings(model="tinyllama")
else:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Save to FAISS DB
db = FAISS.from_documents(chunks, embedding=embeddings)
db.save_local("vectordb", index_name="travelbot")

print("✅ Ingestion complete. Vector store saved to 'vectordb/'")
