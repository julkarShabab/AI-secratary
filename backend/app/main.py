from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.conversations import router as conversations_router
from app.api.auth import router as auth_router
from app.db.session import init_db
from app.tasks.scheduler import start_scheduler, stop_scheduler
import os

app = FastAPI(
    title="AI Secretary",
    description="Agentic AI personal secretary for tech professionals",
    version="0.1.0"
)

allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(conversations_router)
app.include_router(auth_router)


@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ai-secretary-backend",
        "version": "0.1.0"
    }