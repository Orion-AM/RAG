
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
import os

class VectorService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_DB_DIR
        self.embedding_function = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        
        # Ensure directory exists just in case, though Chroma usually handles it
        os.makedirs(self.persist_directory, exist_ok=True)
        
        self.db = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embedding_function
        )

    async def add_documents(self, texts: list[str], metadatas: list[dict] = None):
        # Chroma.add_texts is synchronous, but we wrap it in a service method that could be async
        # For true async in FastAPI with blocking calls, we'd use run_in_threadpool, 
        # but for this stub we keep it simple or assume low latency.
        self.db.add_texts(texts=texts, metadatas=metadatas)

    async def search(self, query: str, k: int = 4):
        # Similarity search
        docs = self.db.similarity_search(query, k=k)
        return docs
