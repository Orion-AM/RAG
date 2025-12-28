import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.apiendpoints import router as api_router

app = FastAPI(title="LegalJudgement-RAG")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the client URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# App startup events
@app.on_event("startup")
async def startup_event():
    # Create temp directory for uploads
    os.makedirs("temp_uploads", exist_ok=True)

# Include the router
app.include_router(api_router)
