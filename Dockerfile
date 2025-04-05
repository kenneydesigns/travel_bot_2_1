FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Upgrade pip and install dependencies
RUN python3 -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Verify installation of critical dependencies
RUN pip show langchain faiss-cpu sentence-transformers transformers accelerate uvicorn fastapi || \
    (echo "❌ Missing dependencies. Check requirements.txt." && exit 1)

# Add /app to PYTHONPATH
ENV PYTHONPATH=/app

# Expose the application port
EXPOSE 8000

# Run the application using the CLI
CMD ["python3", "src/main.py", "server"]