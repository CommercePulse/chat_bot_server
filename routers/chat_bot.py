from fastapi import APIRouter,UploadFile,File,BackgroundTasks,Form
from models.dto import DeleteFileDTO,ChatRequest
from services.bot_namespace_queries import BotNamespaceQueries
from services.chat_bot_service import ChatBot
from typing import List
from services.pinecone_service import PineconeService
router = APIRouter() 

botNamespaceQueries = BotNamespaceQueries()
pineconeService = PineconeService()

chatBotService = ChatBot(botNamespaceQueries,pineconeService)

@router.get("/health")
async def healthCheck():
   return "Ok"

@router.post("")
async def create(name:str):
    return await chatBotService.create(name)

@router.get("")
async def getBot(namespace_id: str):
    return await chatBotService.getBot(namespace_id)

@router.post("/fileUpload")
async def upload(namespace_id: str= Form(...),files: List[UploadFile] = File(...),backgroundTasks: BackgroundTasks = None):
    return await chatBotService.upload_files(namespace_id,files,backgroundTasks)

@router.get("/files")
async def getFiles(namespace_id: str):
    return await chatBotService.get_files(namespace_id)

@router.delete("/files")
async def deleteFiles(data:DeleteFileDTO,backgroundTasks: BackgroundTasks):
    return await chatBotService.delete_files(data,backgroundTasks)

@router.post("/chat")
async def chatConversation(data: ChatRequest):
    return await chatBotService.chat_conversation(data)

# @router.post("/getChats")
# async def getConversation(namespace_id: str):
#     return await chatBotService.get_conversation(namespace_id)

 