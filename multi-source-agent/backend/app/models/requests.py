
from pydantic import BaseModel, Field
from typing import Optional

class UserQuery(BaseModel):
    query: str = Field(..., description="The user's question or request")
    
class DocumentUpload(BaseModel):
    content: str = Field(..., description="The content of the document")
    metadata: Optional[dict] = Field(default={}, description="Optional metadata for the document")
