from enum import Enum
from pydantic import BaseModel 
from typing import List

class DeleteFileDTO(BaseModel):
    namespace_id: str 
    ids: List[int] = None
    names:List[str] = None

class ChatRequest(BaseModel): 
    question: str
    namespace_id: str    
    chatHistory:str 

 
    
class Action(str,Enum):
    PULL = "PULL"
    STOP = "STOP"
    START = "START"
    RESTART = "RESTART"
    STATUS = "STATUS"


       

  
 
     
