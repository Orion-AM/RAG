from celery import Celery
import os
from app.ingestion import ingest_document

# Configure Celery to use Redis as the message broker
celery_app = Celery(
    "legal_worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
)

@celery_app.task(bind=True)
def task_ingest_file(self, file_path: str, file_id: str):
    try:
        chunks_count = ingest_document(file_path, file_id)
        
        # Cleanup local file after processing
        if os.path.exists(file_path):
            os.remove(file_path)
            
        return {"status": "completed", "chunks": chunks_count, "file_id": file_id}
    except Exception as e:
        # In production, log this error to Sentry/Cloudwatch
        return {"status": "failed", "error": str(e)}
