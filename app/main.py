"""
Mentoro RAG API - Main Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import db_manager
from app.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager.connect()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Mentoro RAG API",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://144.79.249.98:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1", tags=["Mentoro RAG API"])


@app.get("/")
def root():
    return {
        "message": "Mentoro RAG is running!",
        "status": "success",
    }