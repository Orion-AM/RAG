
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from app.core.config import settings
from app.services.vector_service import VectorService
from app.services.tools.sql import query_sql_db
from app.services.tools.mongo import query_mongo_db
from langchain_core.tools import Tool

class AgentService:
    def __init__(self, vector_service: VectorService):
        self.vector_service = vector_service
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY)
        self.tools = self._initialize_tools()
        self.agent_executor = self._initialize_agent()

    def _initialize_tools(self):
        # We wrap the vector store search as a tool
        def vector_search_func(query: str):
            # Since tools are sync by default in this context, we'd need a sync wrapper or use Async tools.
            # For simplicity in this sync tool wrapper, we are calling a method that might be async in reality.
            # But here `vector_service.db.similarity_search` is sync.
            # Let's direct call the sync method on the underlying db for the tool
            docs = self.vector_service.db.similarity_search(query)
            return "\n\n".join([d.page_content for d in docs])

        vector_tool = Tool(
            name="VectorSearch",
            func=vector_search_func,
            description="Useful for searching internal documentation and knowledge base."
        )

        return [vector_tool, query_sql_db, query_mongo_db]

    def _initialize_agent(self):
        # Get the prompt to use - using a standard pulling from hwchase17/openai-tools-agent or building one
        # For stability, let's define a simple one or pull a standard one
        prompt = hub.pull("hwchase17/openai-tools-agent")
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    async def process_query(self, query: str) -> dict:
        # Agent execution
        result = await self.agent_executor.ainvoke({"input": query})
        return {
            "answer": result["output"],
            # Since we are using standard ReAct/Tools agent, intermediate steps might not be strictly 'sources' 
            # in the RAG sense unless strictly defined. We'll return a placeholder or parse actions if needed.
            # For this requirement, we will leave sources empty or implement a more complex callback handler later.
            "sources": [] 
        }
