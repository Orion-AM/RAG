import shutil
import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.worker import task_ingest_file
from app.rag import get_answer
from pinecone import Pinecone

router = APIRouter()

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

@router.post("/api/v1/ingest")
async def ingest_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    # Ensure temp directory exists
    os.makedirs("temp_uploads", exist_ok=True)

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

@router.post("/api/v1/query", response_model=QueryResponse)
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
             raise HTTPException(status_code=429, detail="API Quota Exceeded. Please check your billing or try again later.")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/v1/reset")
async def reset_index():
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME")
        index = pc.Index(index_name)
        
        index.delete(delete_all=True)
        
        return {"message": f"All data cleared from index '{index_name}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def health_check():
    return {"status": "Legal RAG Service is running"}
