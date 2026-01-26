
from fastapi import FastAPI
from app.api.v1.query import router as query_router
from app.core.config import settings
import uvicorn

app = FastAPI(
    title="Multi-Source Agent API",
    description="API for multi-source RAG agent",
    version="1.0.0"
)

app.include_router(query_router, prefix="/api/v1", tags=["agent"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
