from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import chat
from app.db.database import engine
from app.db import models
from contextlib import asynccontextmanager
import asyncio
from app.services.rag_service import rag_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize AI in background
    asyncio.create_task(asyncio.to_thread(rag_service.initialize))
    yield
    # Shutdown logic (if any) could go here

# Create Database Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend API for Language-Agnostic Generative AI College Chatbot",
    lifespan=lifespan
)

# Set all CORS enabled origins (Allow ALL for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files & Integrated Frontend
from fastapi.staticfiles import StaticFiles
import os

static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
index_file = os.path.join(static_path, "index.html")

# 1. API Routers
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
from app.api.endpoints import ingest
app.include_router(ingest.router, prefix=f"{settings.API_V1_STR}/ingest", tags=["ingest"])

# 2. Server-side UI serving
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
else:
    @app.get("/")
    async def root():
        return {"error": "UI files not found. Please ensure backend/static folder exists."}

# End of main.py
