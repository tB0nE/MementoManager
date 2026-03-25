from pydantic import BaseModel
from typing import List, Optional, Union

class ChatStoreRequest(BaseModel):
    text: str
    namespace: str = "default"

class TargetedStoreRequest(BaseModel):
    content: str
    type: str # "fact" or "relationship"
    subject: Optional[str] = None
    relation: Optional[str] = None
    object: Optional[str] = None
    namespace: str = "default"

class RetrievalRequest(BaseModel):
    query: str
    namespace: str = "default"

class Relationship(BaseModel):
    subject: str
    relation: str
    object: str

class MemoryResponse(BaseModel):
    facts: List[str]
    relationships: List[Relationship]
    chat_logs: Optional[List[str]] = None

class TargetedResponse(BaseModel):
    answer: str
