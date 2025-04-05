#!/bin/bash

echo "🚀 TravelBot Setup Script"

# Redirect output to a log file
exec > >(tee -i setup.log)
exec 2>&1

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1)
echo "Python version: $python_version"
if [[ "$python_version" != "Python 3.12"* ]]; then
    echo "⚠️ Python 3.12 is required. Current version: $python_version"
    exit 1
fi

# Ensure pip is installed
echo "🔍 Checking if pip is installed..."
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip and try again."
    exit 1
else
    echo "✅ pip is installed."
fi

# Create necessary folders
echo "📂 Creating necessary folders..."
mkdir -p rag/jtr_chunks models web/templates
if [ $? -eq 0 ]; then
    echo "✅ Folders created successfully."
else
    echo "❌ Failed to create folders."
    exit 1
fi

# Create and activate the virtual environment
echo "🐍 Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment created successfully."
    else
        echo "❌ Failed to create virtual environment."
        exit 1
    fi
else
    echo "✅ Virtual environment already exists."
fi

echo "🔍 Checking if virtual environment activation script exists..."
if [ -f ".venv/bin/activate" ]; then
    echo "✅ Activation script found. Activating virtual environment..."
    source .venv/bin/activate
    if [ $? -eq 0 ]; then
        echo "✅ Virtual environment activated successfully."
    else
        echo "❌ Failed to activate virtual environment."
        exit 1
    fi
else
    echo "❌ Activation script not found. Recreate the virtual environment."
    exit 1
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip
if [ $? -eq 0 ]; then
    echo "✅ pip upgraded successfully."
else
    echo "❌ Failed to upgrade pip."
    exit 1
fi

# Install dependencies from requirements.txt
echo "📦 Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully."
    else
        echo "❌ Failed to install dependencies."
        exit 1
    fi
else
    echo "⚠️ requirements.txt not found. Skipping dependency installation."
fi

# Install additional critical packages
echo "📦 Installing additional critical packages..."
pip install langchain_community
if [ $? -eq 0 ]; then
    echo "✅ Critical packages installed successfully."
else
    echo "❌ Failed to install critical packages."
    exit 1
fi

# Verify installation of critical packages
echo "✅ Verifying installed packages..."
for package in langchain-community transformers torch sentence-transformers faiss-cpu PyMuPDF; do
    echo "🔍 Checking if $package is installed..."
    pip show $package > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ $package is installed."
    else
        echo "❌ $package is not installed."
        exit 1
    fi
done

# Run update_knowledge_base.py to process PDFs and create chunks
echo "📄 Running update_knowledge_base.py to process PDFs and create chunks..."
if [ -f "update_knowledge_base.py" ]; then
    python update_knowledge_base.py
    if [ $? -eq 0 ]; then
        echo "✅ update_knowledge_base.py ran successfully."
    else
        echo "❌ Failed to run update_knowledge_base.py."
        exit 1
    fi
else
    echo "⚠️ 'update_knowledge_base.py' not found. Skipping PDF processing."
fi

# Run build_index.py to build the FAISS vector index
echo "🧠 Running build_index.py to build the FAISS vector index..."
if [ -f "build_index.py" ]; then
    python build_index.py --mode all
    if [ $? -eq 0 ]; then
        echo "✅ build_index.py ran successfully."
    else
        echo "❌ Failed to run build_index.py."
        exit 1
    fi
else
    echo "⚠️ 'build_index.py' not found. Skipping index build."
fi

# Check for .env file and create a default one if missing
echo "🔍 Checking for .env file..."
if [ ! -f ".env" ]; then
    echo "🌱 Creating default .env file..."
    cat <<EOL > .env
MODEL_ID=google/flan-t5-small
PORT=8000
EOL
    echo "✅ Default .env file created."
else
    echo "✅ .env file found."
fi

echo ""
echo "✅ Setup complete."
echo "👉 To start locally: source .venv/bin/activate && python app.py"
echo "👉 To start with Docker: docker-compose up --build"