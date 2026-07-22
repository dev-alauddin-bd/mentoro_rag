"""
API v1 Routes
Defines all endpoints for the Mentoro RAG API, including streaming pipelines.
"""

import json
from fastapi import APIRouter, HTTPException, status
import os
from fastapi.responses import StreamingResponse # Critical import for handling continuous buffered generation
from app.validation.schemas import (
    QueryRequest, QueryResponse,
    PlatformInfoRequest,
    CourseContentRequest,
    StudentMemoryRequest,
    BulkSyncRequest, BulkSyncResponse,
    SyncSourceRequest,
    GenerateCourseContentRequest, GenerateCourseContentResponse,
    GenerateLiveSessionRequest, GenerateLiveSessionResponse
)
from app.services.rag_service import RAGService
from app.services.sync_service import SyncService
from app.services.generation_service import GenerationService
from app.config.database import db_manager

router = APIRouter()

# =========================================================================
# CHAT ENDPOINT (STREAMING CHANNELS VIA SSE)
# =========================================================================

@router.post("/chat", status_code=status.HTTP_200_OK)
async def chat(request_data: QueryRequest):
    """
    Main asynchronous chat endpoint. Translates and optimizes queries, fetches matching 
    context documents, and pipes non-buffered token chunks down to client components via SSE.
    """
    # Defensive programming: Terminate blank or spacing payload strings early
    if not request_data.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Step 1: Execute query restructuring via LLM prompt formatting
        optimized_query = await RAGService.optimize_query(request_data.question)

        # Step 2: Extract historical/vector context vectors from core vector repository
        retrieved_docs = await RAGService.retrieve_context(
            optimized_query=optimized_query,
            course_id=request_data.course_id,
            student_id=request_data.student_id
        )

        # Step 3: Define Server-Sent Events (SSE) background stream engine wrapper
        async def event_generator():
            try:
                # Stage A: Ship processing metadata objects immediately before generation delay
                initial_metadata = {
                    "status": "success",
                    "original_query": request_data.question,
                    "optimized_query": optimized_query,
                    "context_retrieved": retrieved_docs
                }
                # Structured compliance syntax required for proper JS EventSource mapping (\n\n)
                yield f"data: {json.dumps({'type': 'metadata', 'content': initial_metadata})}\n\n"

                # Stage B: Pipe active generated token streams smoothly down the TCP pipe
                async for token in RAGService.generate_response(optimized_query, retrieved_docs):
                    yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
                    
            except Exception as stream_err:
                # Graceful handling of execution disruptions mid-stream
                yield f"data: {json.dumps({'type': 'error', 'content': str(stream_err)})}\n\n"

        # Initialize network engine stream handling via proper text/event-stream media configurations
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    except Exception as e:
        # Catch unexpected RAG failures prior to stream configuration steps
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# =========================================================================
# DATA INGESTION ENDPOINTS
# =========================================================================

@router.post("/platform-info", status_code=status.HTTP_201_CREATED)
async def add_platform_info(data: PlatformInfoRequest):
    """Ingest platform info / FAQ into ChromaDB."""
    if not data.document.strip():
        raise HTTPException(status_code=400, detail="Document cannot be empty.")

    try:
        db_manager.platform_info_store.add_texts(
            texts=[data.document],
            metadatas=[{"category": data.category.lower(), "type": "platform_general"}]
        )
        return {"status": "success", "message": "Platform info saved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/course-content", status_code=status.HTTP_201_CREATED)
async def add_course_content(data: CourseContentRequest):
    """Ingest single course content into ChromaDB."""
    if not data.document.strip():
        raise HTTPException(status_code=400, detail="Document cannot be empty.")

    try:
        metadata = {"course_id": data.course_id}

        if data.title:
            metadata["title"] = data.title
        if data.category:
            metadata["category"] = data.category
        if data.price is not None:
            metadata["price"] = str(data.price)
        if data.instructor:
            metadata["instructor"] = data.instructor
        if data.slug:
            metadata["slug"] = data.slug
        if data.level:
            metadata["level"] = data.level
        if data.duration:
            metadata["duration"] = data.duration
        if data.tags:
            metadata["tags"] = data.tags
        if data.language:
            metadata["language"] = data.language

        db_manager.course_contents_store.add_texts(
            texts=[data.document],
            metadatas=[metadata]
        )
        return {
            "status": "success",
            "message": f"Course content saved for {data.course_id}.",
            "metadata_stored": list(metadata.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/student-memories", status_code=status.HTTP_201_CREATED)
async def add_student_memory(data: StudentMemoryRequest):
    """Ingest student memory / note into ChromaDB."""
    if not data.document.strip():
        raise HTTPException(status_code=400, detail="Document cannot be empty.")

    try:
        db_manager.student_memories_store.add_texts(
            texts=[data.document],
            metadatas=[{"student_id": data.student_id}]
        )
        return {"status": "success", "message": f"Memory saved for student {data.student_id}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-courses", status_code=status.HTTP_200_OK)
async def sync_all_courses(data: BulkSyncRequest):
    """Bulk sync courses from Node.js/PostgreSQL into ChromaDB."""
    result = await SyncService.sync_courses(data.courses)
    return BulkSyncResponse(**result)


# =========================================================================
# CONTENT & LIVE SESSION GENERATION ENDPOINTS
# =========================================================================

@router.post("/generate-course-content", response_model=GenerateCourseContentResponse, status_code=status.HTTP_200_OK)
async def generate_course_content(data: GenerateCourseContentRequest):
    """Generate structured course metadata using LLM."""
    if not data.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    try:
        content_data = await GenerationService.generate_course_content(data.topic)
        return GenerateCourseContentResponse(status="success", data=content_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate course content: {str(e)}")


@router.post("/generate-live-session", response_model=GenerateLiveSessionResponse, status_code=status.HTTP_200_OK)
async def generate_live_session(data: GenerateLiveSessionRequest):
    """Generate structured live session details using LLM."""
    if not data.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty.")

    try:
        session_data = await GenerationService.generate_live_session(data.title)
        return GenerateLiveSessionResponse(status="success", data=session_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate live session: {str(e)}")

