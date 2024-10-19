from enum import Enum
from pydantic import BaseModel 
from typing import List

class DeleteFileDTO(BaseModel):
    namespace_id: str 
    ids: List[int] = None
    names:List[str] = None

class conversation(BaseModel): 
    question: str
    Ai_response: str  
    
class ChatRequest(BaseModel): 
    question: str
    namespace_id: str    
    chatHistory:List[conversation] 

class Action(str,Enum):
    PULL = "PULL"
    STOP = "STOP"
    START = "START"
    RESTART = "RESTART"
    STATUS = "STATUS"


       

  
 
     
