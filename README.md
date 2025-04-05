# TravelBot

**TravelBot** is an automated assistant designed to process Air Force travel regulations, extract relevant information, and provide quick answers to PCS-related questions. It uses advanced AI models and a FAISS vector database for efficient retrieval.

---

## ✨ Features

- 📄 **Auto-Chunking**: Automatically processes uploaded `.pdf` files into manageable text chunks.
- 🔍 **Regulation Search**: Uses FAISS and LangChain to retrieve relevant sections from JTR, DAFI 36-3003, and AFMAN 65-114.
- 🤖 **Three Modes of Assistance**:
  - **Simple Bot**: Quick answers using a basic LLM.
  - **Chunk Bot**: Retrieves relevant regulation chunks directly.
  - **Context Bot**: Combines chunk retrieval with conversational responses and source references.
- 📂 **Dynamic Knowledge Base**: Easily update the bot with new regulations by uploading PDFs.
- ⚡ **Flexible Deployment**: Works locally or in GitHub Codespaces, with support for Hugging Face and Ollama LLMs.

---

## 🛠️ Dev Container Tools

This dev container comes pre-installed with several tools to support both Node.js and Python development as well as container management:
- **Node.js Tools**: `node`, `npm` and `eslint` are available on the `PATH` for JavaScript development.
- **Python Tools**: `python3` and `pip3` are pre-installed along with Python language extensions.
- **Container Tools**: The Docker CLI (`docker`) is available for running and managing containers.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/travelbot.git
cd travelbot
```
or

use Visual Studio Code's **Codespaces** <> Code feature to create a codespace on the `main` branch.

### 2. Run the setup script:
```bash
bash [setup.sh](http://_vscodecontentref_/1)
```
### 3. Then activate your environment and run the chatbot:
```bash
source .venv/bin/activate
python [travelbot.py](http://_vscodecontentref_/2) --mode context
```

💡 If you’re testing from a fresh environment, this flow ensures everything is installed and indexed before your first question.

---

🧠 How to Use TravelBot
-   ✅ Option 1: `travelbot.py` – Unified CLI Chatbot  
    Supports three modes:

    --mode simple: Uses a basic LLM for quick answers.  
    --mode chunk: Retrieves relevant regulation chunks directly.  
    --mode context: Combines chunk retrieval with conversational responses and source references.
    ```bash
    python [travelbot.py](http://_vscodecontentref_/3) --mode simple
    python [travelbot.py](http://_vscodecontentref_/4) --mode chunk
    python [travelbot.py](http://_vscodecontentref_/5) --mode context
    ```

-   ✅ Option 2: `chunkbot.py` – Search-Only Tool  
    No LLM used  
    Retrieves top regulation chunks directly  
    Great for debugging or validation
    ```bash
    python [chunkbot.py](http://_vscodecontentref_/6)
    ```

-   ✅ Option 3: `simple_bot.py` – Prompt-Controlled Chatbot  
    Loads system prompt + tone guidance from context/  
    Uses LangChain's RetrievalQA chain  
    Token-limited, clean, predictable
    ```bash
    python [app.py](http://_vscodecontentref_/7)
    ```

---

🔄 Updating the Regulation Knowledge Base  
When JTR or DAFI updates:

Drop PDFs into:
```bash
rag/source_docs/
```
Run:
```bash
python src/update_knowledge_base.py
```
This extracts text, chunks it with RecursiveCharacterTextSplitter, and rebuilds the FAISS vector index.

---

🧰 Folder Structure
```bash
├── src/
│   ├── [travelbot.py](http://_vscodecontentref_/8)          # Main entry point for all modes
│   ├── [app.py](http://_vscodecontentref_/9)                # Simple bot
│   ├── [chunkbot.py](http://_vscodecontentref_/10)           # Chunk retriever bot
│   ├── [update_knowledge_base.py](http://_vscodecontentref_/11) # Updates the FAISS vector database
│   ├── context/              # Optional .txt files for system prompt and tone
│   └── rag/
│       ├── source_docs/      # PDFs for regulation updates
│       └── jtr_chunks/       # Chunked regulation text
├── vectordb/                 # FAISS vector database
├── [requirements.txt](http://_vscodecontentref_/12)          # Python dependencies
├── [setup.sh](http://_vscodecontentref_/13)                  # Environment setup script
└── [README.md](http://_vscodecontentref_/14)                 # Project documentation
```

---

🤖 Experimenting with LLMs  
Use a Hugging Face model:  
- Inside `travelbot.py` or `app.py`, update:
```bash
MODEL_ID = "google/flan-t5-small"  # or flan-t5-base
```

Use local Ollama:
1. Install Ollama
2. Pull a model:
```bash
ollama pull tinyllama
```
Modify `setup.sh` or `travelbot.py` to load the Ollama LLM instead of Hugging Face.

---

📘 Source Materials  
TravelBot can index and respond based on:
- JTR (March 2025)
- DAFI 36-3003 (August 2024)
- AFMAN 65-114 (current)
- Any `.pdf` you drop into `rag/source_docs/`

### 🔄 Managing the FAISS Vector Database

#### Build the Initial Index  
To process all chunks and build the initial FAISS vector database:
```bash
python [build_index.py](http://_vscodecontentref_/8) --mode all
```
---

📅 Roadmap
-   <input disabled="" type="checkbox"> Add Gradio or FastAPI web UI
-   <input disabled="" type="checkbox"> Add chat memory / history
-   <input disabled="" type="checkbox"> Add evaluator scoring / confidence indicator
-   <input disabled="" type="checkbox"> Add embedded link-back to reg source section

---

🙌 Contributing  
Fork it, remix it, deploy it at your unit.  
TravelBot is built to help Airmen and DoD staff get answers without combing through thousands of pages.
"""

print("README.md has been generated successfully!")