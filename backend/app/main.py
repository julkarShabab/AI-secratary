from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
import os

app = FastAPI(
    title="AI Secretary",
    description="Agentic AI personal secretary for tech professionals",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(upload_router)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-secretary-backend",
        "version": "0.1.0"
    }