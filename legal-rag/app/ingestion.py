import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from dotenv import load_dotenv

load_dotenv()

# Initialize Embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def ingest_document(file_path: str, file_id: str):
    """
    1. Load PDF
    2. Split into chunks
    3. Embed and Upsert to Pinecone
    """
    
    # 1. Load PDF (PyMuPDF automatically grabs page_number metadata)
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    
    # Add the filename/file_id to metadata for every page
    for doc in documents:
        doc.metadata["filename"] = file_id

    # 2. Split Text (Chunking)
    # 1000 chars ~ 200-250 tokens. Overlap ensures context isn't lost at cut-offs.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    splits = text_splitter.split_documents(documents)
    print(f"Created {len(splits)} chunks for {file_id}")

    # 3. Embed & Store in Pinecone
    # LangChain handles the batching and embedding calls automatically here.
    PineconeVectorStore.from_documents(
        documents=splits,
        embedding=embeddings,
        index_name=os.getenv("PINECONE_INDEX_NAME")
    )
    
    return len(splits)
