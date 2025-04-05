import argparse
import sys

def run_server():
    # Launch your FastAPI app using uvicorn
    # Adjust the module path if needed (e.g., "src.web_app:app")
    import uvicorn
    uvicorn.run("src.web_app:app", host="127.0.0.1", port=8000, reload=True)

def run_ingestion():
    # Import your ingestion logic (ensure a function exists to call)
    from ingest import start_ingestion  # Ensure start_ingestion is defined in ingest.py
    start_ingestion()

def build_index():
    # Import your build index logic (ensure a function exists to call)
    from build_index import create_index  # Ensure create_index is defined in build_index.py
    create_index()

def main():
    parser = argparse.ArgumentParser(
        description="Travel Bot - Command Line Interface"
    )
    parser.add_argument(
        "command",
        choices=["server", "ingest", "build-index"],
        help="Command to execute: 'server' to launch the web app, 'ingest' to run ingestion, or 'build-index' to build the vector index."
    )
    args = parser.parse_args()

    if args.command == "server":
        run_server()
    elif args.command == "ingest":
        run_ingestion()
    elif args.command == "build-index":
        build_index()
    else:
        print("Unknown command")
        sys.exit(1)

if __name__ == "__main__":
    main()