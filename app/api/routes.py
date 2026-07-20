"""
API v1 Routes
Defines all endpoints for the Mentoro RAG API.
"""

from fastapi import APIRouter, HTTPException, status
from app.validation.schemas import (
    QueryRequest, QueryResponse,
    PlatformInfoRequest,
    CourseContentRequest,
    StudentMemoryRequest,
    BulkSyncRequest, BulkSyncResponse
)
from app.services.rag_service import RAGService
from app.services.sync_service import SyncService
from app.config.database  import db_manager

router = APIRouter()

# =========================================================================
# CHAT ENDPOINT
# =========================================================================

@router.post("/chat", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def chat(request_data: QueryRequest):
    """
    Main chat endpoint. Optimizes query, retrieves context, generates response.
    """
    if not request_data.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        # Step 1: Optimize query
        optimized_query = await RAGService.optimize_query(request_data.question)

        # Step 2: Retrieve context
        retrieved_docs = await RAGService.retrieve_context(
            optimized_query=optimized_query,
            course_id=request_data.course_id,
            student_id=request_data.student_id
        )

        # Step 3: Generate response
        ai_response = await RAGService.generate_response(optimized_query, retrieved_docs)

        return QueryResponse(
            status="success",
            original_query=request_data.question,
            optimized_query=optimized_query,
            context_retrieved=retrieved_docs,
            ai_response=ai_response
        )

    except Exception as e:
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
