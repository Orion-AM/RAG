
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.requests import UserQuery
from app.models.responses import AgentResponse
from app.services.agent_service import AgentService
from app.services.vector_service import VectorService
import time

router = APIRouter()

def get_vector_service():
    return VectorService()

def get_agent_service(vector_service: VectorService = Depends(get_vector_service)):
    return AgentService(vector_service=vector_service)

@router.post("/chat", response_model=AgentResponse)
async def chat(
    query: UserQuery,
    agent_service: AgentService = Depends(get_agent_service)
):
    start_time = time.time()
    try:
        result = await agent_service.process_query(query.query)
        execution_time = time.time() - start_time
        
        return AgentResponse(
            answer=result["answer"],
            sources=result["sources"],
            execution_time=execution_time
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
