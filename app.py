from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat_bot
 
from config.sqlite  import init_db
from utils.exception import CustomExceptionHandler
app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost",
    "http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CustomExceptionHandler)

# init_db()

# @app.get("/healthCheck")
# async def read_root():
#     return {"message": "Server is Running"}


app.include_router(chat_bot.router,
    prefix="/chat-bot",
    tags=["ChatBot"])

 

