# LegalJudgement-RAG

A Retrieval-Augmented Generation (RAG) system for legal judgments using FastAPI, LangChain, Celery, and Pinecone.

## Features

-   **PDF Ingestion**: Upload legal judgment PDFs.
-   **Background Processing**: Uses Celery to handle large files asynchronously.
-   **Semantic Search**: Uses Google Gemini embeddings and Pinecone for vector search.
-   **RAG Querying**: Ask questions about the judgments and get answers with citations.

## Setup

1.  **Clone the repository** (if applicable).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    -   Rename `.env` (if it's a template) or ensure it exists.
    -   Fill in your API keys:
        ```env
        GOOGLE_API_KEY=your_google_gemini_api_key
        PINECONE_API_KEY=your_pinecone_api_key
        PINECONE_INDEX_NAME=legal-judgement-index
        CELERY_BROKER_URL=redis://localhost:6379/0
        ```

## Running the Application

1.  **Start Redis** (Required for Celery):
    ```bash
    docker run -d -p 6379:6379 redis
    ```

2.  **Start the Celery Worker**:
    ```bash
    celery -A app.worker.celery_app worker --loglevel=info
    ```

3.  **Start the FastAPI Server**:
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

1.  **Open the UI**:
    -   Simply open `client/index.html` in your web browser.
    -   Or serve it using a simple HTTP server:
        ```bash
        cd client
        python -m http.server 3000
        ```
        Then visit `http://localhost:3000`.

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
