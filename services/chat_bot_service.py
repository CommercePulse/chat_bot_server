import pprint
import uuid
from utils.success import result,success
from models.schemas import BotVectorNamespace,BotNamespaceFiles
from utils.helper import save_uploaded_file
from fastapi import  BackgroundTasks
from dotenv import load_dotenv
import os
import json
load_dotenv()
from fastapi.responses import StreamingResponse
os.environ["LANGCHAIN_PROJECT"] = "CHATBOT"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"]= os.getenv("LANGCHAIN_API_KEY")

class ChatBot:
    
    def __init__(self,botNamespaceQueries,pineconeService):
        self.botNamespaceQueries = botNamespaceQueries
        self.pineconeService = pineconeService

    async def create(self,name):
        namespace_id = str(uuid.uuid4())
        bot_instance = BotVectorNamespace(
                       bot_name=name,
                       namespace_id=namespace_id,
                       namespace_name="Default"  # If this is constant, no need to make it dynamic
                        )
        
        await self.botNamespaceQueries.execute_create_command(bot_instance)
        return result({"message": "Congratulations, your created your bot", "namespace_id": namespace_id})
    
    async def getBot(self,namespace_id): 
       return await self.botNamespaceQueries.get_bot_info(namespace_id)

    async def upload_files(self,namespace_id,files,backgroundTasks:BackgroundTasks):
         
        if len(files):
            for file in files: 
                save_uploaded_file(file, namespace_id)
                file_instance = BotNamespaceFiles(
                       name=file.filename,
                       namespace_id=namespace_id,
                       size=file.size,  
                        )
        
                await self.botNamespaceQueries.execute_create_command(file_instance)
                backgroundTasks.add_task(self.pineconeService.vectorize_documents_main,namespace_id)
                # await self.pineconeService.vectorize_documents_main(namespace_id)

        return success(f"Total {len(files)} files uploaded successfully!")
    
    async def get_files(self,namespace_id): 
       return await self.botNamespaceQueries.get_file_info(namespace_id)
    
    async def delete_files(self,data,backgroundTasks:BackgroundTasks): 
            await self.botNamespaceQueries.delete_files(data.ids)
            backgroundTasks.add_task(self.pineconeService.delete_vectorized_docs,data.namespace_id,"name",data.names)
            return success("File deleted Successfully!")
    
    async def chat_conversation(self,data):  
            question = data.question
            namespace_id = data.namespace_id
              
            # if isinstance(data.chatHistory, str):
            #    data.chatHistory = json.loads(data.chatHistory.replace("'", '"')) 

            chatHistory = ""
            for chat in data.chatHistory:
                chatHistory += f"User: {chat.question}\nAI: {chat.Ai_response}\n"

            return StreamingResponse(self.pineconeService.chain_resp(namespace_id,question,chatHistory), media_type="text/event-stream")
    
    async def get_conversation(self,namespace_id): 
        return await self.botNamespaceQueries.get_chat_interaction(namespace_id)




    


