
from langchain_core.tools import tool

@tool
def query_mongo_db(query: str) -> str:
    """Useful for querying the MongoDB database.
    Use this tool when you need to fetch unstructured logs or event data.
    """
    # Create valid dummy response that mimics Mongo result
    return f"Result for query '{query}': {{'event_id': 'evt_123', 'type': 'login', 'timestamp': '2023-10-27T10:00:00Z'}}"
