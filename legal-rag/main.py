import shutil
import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.worker import task_ingest_file
from app.rag import get_answer

app = FastAPI(title="LegalJudgement-RAG")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the client URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create temp directory for uploads
os.makedirs("temp_uploads", exist_ok=True)

# --- Data Models ---
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class Citation(BaseModel):
    source: str
    page: int
    chunk_text_snippet: str

class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]

# --- Endpoints ---

@app.post("/api/v1/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # Generate unique ID and save locally
    file_id = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"temp_uploads/{file_id}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Trigger Celery Task (Background)
    task = task_ingest_file.delay(file_path, file_id)

    return {
        "message": "Ingestion started",
        "task_id": task.id,
        "file_id": file_id
    }

@app.post("/api/v1/query", response_model=QueryResponse)
async def query_index(request: QueryRequest):
    try:
        # Call the RAG chain
        result = get_answer(request.query)
        
        # Format Citations from the retrieved context
        citations = []
        for doc in result["context"]:
            citations.append(Citation(
                source=doc.metadata.get("filename", "unknown"),
                # Default to page 1 if metadata missing
                page=int(doc.metadata.get("page", 0)) + 1, 
                # First 100 chars as snippet
                chunk_text_snippet=doc.page_content[:100] + "..." 
            ))

        return {
            "answer": result["answer"],
            "citations": citations
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        if "429" in str(e):
             raise HTTPException(status_code=429, detail="Google Gemini API Quota Exceeded. Please check your billing or try again later.")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    return {"status": "Legal RAG Service is running"}
