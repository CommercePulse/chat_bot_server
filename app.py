from fastapi import FastAPI
from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from routers import chat_bot
# from mangum import Mangum
from config.sqlite  import init_db
from fastapi.staticfiles import StaticFiles
from utils.exception import CustomExceptionHandler
from models.creation import TableCreation
app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.mount("/static", StaticFiles(directory="dist", html=True), name="static")

# # Optional: Redirect from `/` to `/static/index.html`
# @app.get("/")
# async def root():
#     return RedirectResponse(url="/static/index.html")
app.add_middleware(CustomExceptionHandler)
init_db()
app.include_router(chat_bot.router,
    prefix="/chat-bot",
    tags=["ChatBot"])
app.mount("/", StaticFiles(directory="dist", html=True), name="dist")


# handler = Mangum(app)


