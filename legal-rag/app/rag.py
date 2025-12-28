import os
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Setup Vector Store Connection (for reading)
# Using 'gemma' for embeddings
embeddings = OllamaEmbeddings(
    model="embeddinggemma", 
    base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
)
vectorstore = PineconeVectorStore(
    index_name=os.getenv("PINECONE_INDEX_NAME"),
    embedding=embeddings
)

# Setup LLM (Ollama - gemma3:4b)
llm = ChatOllama(
    model="gemma3:4b", 
    temperature=0.1,
    base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
)

# 1. Define the RAG Prompt  
# We strictly instruct the model to use ONLY the context.
system_prompt = (
    "You are a legal assistant. Use the following pieces of retrieved context to answer "
    "the question. If the answer is not in the context, say 'Answer not found in provided documents'. "
    "Do not hallucinate. \n\n"
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# 2. Create the Chain
question_answer_chain = create_stuff_documents_chain(llm, prompt)
retriever = vectorstore.as_retriever(search_kwargs={"k": 5}) # Top 5 chunks
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

def get_answer(query: str):
    """
    Executes the RAG pipeline.
    Returns: answer string AND source documents (for citations).
    """
    response = rag_chain.invoke({"input": query})
    return {
        "answer": response["answer"],
        "context": response["context"] # Contains metadata (page, file)
    }
