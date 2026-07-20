"""
Mentoro RAG API - Main Application Entry Point
Production-grade FastAPI application with LangChain, Groq LLM, and ChromaDB Cloud.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.database import db_manager
from app.api.routes import router as api_router

#  Manage backend initialization routines via Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize ChromaDB connection

    db_manager.connect()
    
    # Yield control to the application
    yield   


# fastapi application instance with lifespan management
app= FastAPI(lifespan=lifespan, title="Mentoro RAG API", version="1.0.0")


app.include_router(api_router, prefix="/api/v1", tags=["Mentoro RAG API"])

# root endpoint
@app.get('/')
def root():
    return {
        "message": "Mentoro RAG is running!",
        "status": "success"
    }





