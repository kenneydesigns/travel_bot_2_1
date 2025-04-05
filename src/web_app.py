from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from travelbot import hybrid_response, load_model_and_retriever

# Initialize FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates directory
templates = Jinja2Templates(directory="templates")

# Load the model and retriever once during app initialization
llm, retriever = load_model_and_retriever()

@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    """Render the main form page."""
    return templates.TemplateResponse("form.html", {"request": request, "answer": None})

@app.post("/", response_class=HTMLResponse)
async def handle_query(request: Request, query: str = Form(...)):
    """Handle the user's query and return the response."""
    try:
        if not query.strip():
            answer = "⚠️ Please enter a valid question."
        else:
            answer = hybrid_response(query, llm, retriever)
    except Exception as e:
        answer = f"❌ An error occurred while processing your query: {e}"

    return templates.TemplateResponse("form.html", {"request": request, "answer": answer, "query": query})