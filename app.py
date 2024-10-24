from fastapi import FastAPI,Request
from typing import Union
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from routers import chat_bot
# from mangum import Mangum
from config.sqlite  import init_db
from fastapi.staticfiles import StaticFiles
from utils.exception import CustomExceptionHandler
from models.creation import TableCreation
import os
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(swagger_ui_parameters={"displayRequestDuration": True})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CustomExceptionHandler)
init_db()
app.include_router(chat_bot.router,
    prefix="/chat-bot",
    tags=["ChatBot"])


app.mount("/", StaticFiles(directory="dist", html=True), name="dist")

# Custom middleware to serve `index.html` for client-side routing
class SPAStaticFilesMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        file_path = os.path.join("dist", path.lstrip("/"))

        # If the file exists in the "dist" directory, serve it
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)

        # If the file doesn't exist, serve the `index.html` file
        if not path.startswith("/chat-bot"):  # Ensure API routes aren't affected
            return FileResponse(os.path.join("dist", "index.html"))

        # Otherwise, continue with the request (for APIs, etc.)
        response = await call_next(request)
        return response


# Add the middleware to handle client-side routing
app.add_middleware(SPAStaticFilesMiddleware)


# handler = Mangum(app)


