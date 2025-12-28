# LegalJudgement-RAG

A Retrieval-Augmented Generation (RAG) system for legal judgments using FastAPI, LangChain, Celery, and Pinecone.

## Features

-   **PDF Ingestion**: Upload legal judgment PDFs.
-   **Background Processing**: Uses Celery to handle large files asynchronously.
-   **Semantic Search**: Uses Google Gemini embeddings and Pinecone for vector search.
-   **RAG Querying**: Ask questions about the judgments and get answers with citations.

## Configuration & Prerequisites

### 1. Prerequisites
- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**: For running the application in containers.
- **[Ollama](https://ollama.com/)**: Must be installed and running on your host machine to provide LLM and embedding services.
- **Pinecone Account**: For vector storage.

### 2. Prepare Ollama Models
Pull the specific models used by the application:
```bash
ollama pull gemma3:4b
ollama pull embeddinggemma
```

### 3. Environment Setup
Create a `.env` file in the root directory.
```bash
# .env content
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=legal-judgement-index
```
*Note: `CELERY_BROKER_URL` and `OLLAMA_BASE_URL` are automatically configured in `docker-compose.yml`.*

### 4. Pinecone Index Setup
- Log in to [Pinecone Console](https://app.pinecone.io/).
- Create a new index:
    - **Name**: `legal-judgement-index` (Must match `.env`)
    - **Dimensions**: `768` (for `embeddinggemma`)
    - **Metric**: `cosine`

## Application Setup (Docker Recommended)

### Option A: Run with Docker
This is the easiest way to get the full stack (Redis, Worker, Backend, Client) running.

1.  **Build and Start**:
    ```bash
    docker-compose up --build
    ```
2.  **Access Components**:
    - **Web Interface**: `http://localhost:3000`
    - **API Docs**: `http://localhost:8000/docs`

### Option B: Run Manually (Local Development)
If you prefer running services individually:

1.  **Install Python Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start Redis**:
    ```bash
    docker run -d -p 6379:6379 redis
    ```

3.  **Start Celery Worker**:
    ```bash
    celery -A app.worker.celery_app worker --loglevel=info
    ```

4.  **Start API Server**:
    ```bash
    uvicorn main:app --reload
    ```

## Usage

-   **Ingest a PDF**:
    -   `POST http://localhost:8000/api/v1/ingest`
    -   Form Data: `file=@your_judgment.pdf`

-   **Query**:
    -   `POST http://localhost:8000/api/v1/query`
    -   JSON Body: `{"query": "What was the verdict?"}`

## Client UI

A modern web interface is available in the `client/` directory.

### Accessing the UI
- **Docker**: Visit `http://localhost:3000`.
- **Manual**: 
    - Serve it using a simple HTTP server:
        ```bash
        cd client
        python -m http.server 3000
        ```
    - Or simply open `client/index.html` in your web browser.

2.  **Use the UI**:
    -   **Upload**: Drag and drop a PDF file to ingest it.
    -   **Query**: Type your question and hit enter to get an answer with citations.

## Project Structure

```
legal-rag/
├── .env                    # API Keys and Secrets
├── requirements.txt        # Python dependencies
├── main.py                 # FastAPI Entry point
├── app/
│   ├── ingestion.py        # LangChain logic for PDF -> Vector
│   ├── rag.py              # LangChain logic for Query -> Answer
│   ├── worker.py           # Celery background task handler
│   └── __init__.py
└── temp_uploads/           # Temporary storage for uploaded PDFs
```
