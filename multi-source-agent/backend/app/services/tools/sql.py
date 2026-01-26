
from langchain_core.tools import tool

@tool
def query_sql_db(query: str) -> str:
    """Useful for querying the SQL database. 
    Use this tool when you need to fetch structured data about users or transactions.
    """
    # Create valid dummy response that mimics SQL result
    return f"Result for query '{query}': [{{'id': 1, 'name': 'John Doe', 'email': 'john@example.com'}}]"
