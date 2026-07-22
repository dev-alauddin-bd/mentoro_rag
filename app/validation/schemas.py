"""
Pydantic Data Models for Request/Response Validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class QueryRequest(BaseModel):
    """Request schema for chat endpoint."""
    question: str = Field(..., description="Raw query string (may be Banglish).")
    course_id: Optional[str] = Field(default=None, description="Filter by course ID.")
    student_id: Optional[str] = Field(default=None, description="Filter by student ID.")

class QueryResponse(BaseModel):
    """Response schema for chat endpoint."""
    status: str
    original_query: str
    optimized_query: str
    context_retrieved: List[str]
    ai_response: str

class PlatformInfoRequest(BaseModel):
    """Request schema for adding platform info / FAQ."""
    document: str = Field(..., description="Platform info or FAQ text.")
    category: str = Field(default="general", description="Category: faq, support, terms, rules.")

class CourseContentRequest(BaseModel):
    """Request schema for adding single course content."""
    document: str = Field(..., description="Course content text.")
    course_id: str = Field(..., description="Unique course identifier.")
    title: Optional[str] = Field(default=None, description="Course title.")
    category: Optional[str] = Field(default=None, description="Course category.")
    price: Optional[float] = Field(default=None, description="Course price.")
    instructor: Optional[str] = Field(default=None, description="Instructor name.")
    slug: Optional[str] = Field(default=None, description="URL slug.")
    level: Optional[str] = Field(default=None, description="Difficulty level.")
    duration: Optional[str] = Field(default=None, description="Course duration.")
    tags: Optional[str] = Field(default=None, description="Comma-separated tags.")
    language: Optional[str] = Field(default=None, description="Course language.")

class StudentMemoryRequest(BaseModel):
    """Request schema for adding student memory / note."""
    document: str = Field(..., description="Student note or memory text.")
    student_id: str = Field(..., description="Unique student identifier.")

class CourseData(BaseModel):
    """Schema for course data coming from Node.js/PostgreSQL."""
    id: str = Field(..., description="Course UUID from PostgreSQL")
    title: str = Field(..., description="Course title")
    description: str = Field(..., description="Course full description")
    category: str = Field(..., description="Course category")
    price: float = Field(..., description="Course price")
    instructor: Optional[str] = Field(default="Instructor", description="Instructor name")
    slug: Optional[str] = Field(default=None, description="URL slug")
    level: Optional[str] = Field(default=None, description="beginner/intermediate/advanced")
    duration: Optional[str] = Field(default=None, description="Course duration")
    tags: Optional[str] = Field(default=None, description="Comma-separated tags")
    language: Optional[str] = Field(default=None, description="Course language")
    enrollment_count: Optional[int] = Field(default=None, description="Number of enrollments")

class BulkSyncRequest(BaseModel):
    """Request schema for bulk course sync."""
    courses: List[CourseData] = Field(..., description="List of courses to sync into ChromaDB")

class BulkSyncResponse(BaseModel):
    """Response schema for bulk sync operation."""
    status: str
    total_processed: int
    successful: int
    failed: int
    details: List[dict]

class SyncSourceRequest(BaseModel):
    """Request schema for syncing all courses from an external source URL."""
    source_url: str = Field(..., description="Full URL of the external course data endpoint returning JSON array of CourseData")


# =========================================================================
# CONTENT GENERATION SCHEMAS
# =========================================================================

class GenerateCourseContentRequest(BaseModel):
    """Request schema for course content generation."""
    topic: str = Field(..., description="Topic or title outline for course generation.")

class GeneratedCourseContentData(BaseModel):
    """Structured response schema for generated course content."""
    title: str = Field(description="Catchy title for the course")
    shortDescription: str = Field(description="Short course summary")
    description: str = Field(description="Detailed course description")
    seoTitle: str = Field(description="SEO optimized title tag")
    seoDescription: str = Field(description="SEO meta description")
    tags: List[str] = Field(default_factory=list, description="List of relevant tags")
    learningOutcomes: List[str] = Field(default_factory=list, description="Key learning outcomes")
    requirements: List[str] = Field(default_factory=list, description="Course prerequisites")
    targetAudience: List[str] = Field(default_factory=list, description="Target audience groups")
    level: str = Field(default="BEGINNER", description="Difficulty level: BEGINNER, INTERMEDIATE, ADVANCED")
    language: str = Field(default="English", description="Language of instruction")
    duration: int = Field(default=60, description="Estimated total duration in minutes")
    categorySuggestion: str = Field(description="Suggested course category")
    thumbnailPrompt: str = Field(description="AI image generation prompt for course thumbnail")

class GenerateCourseContentResponse(BaseModel):
    """Response wrapper for course content generation."""
    status: str = "success"
    data: GeneratedCourseContentData

class GenerateLiveSessionRequest(BaseModel):
    """Request schema for live session outline generation."""
    title: str = Field(..., description="Title or topic of the live session.")

class GeneratedLiveSessionData(BaseModel):
    """Structured response schema for generated live session."""
    title: str = Field(description="Live session title")
    fullDescription: str = Field(description="Detailed description of the live session")
    learningOutcomes: List[str] = Field(default_factory=list, description="Key takeaways or learning outcomes")
    whoShouldAttend: List[str] = Field(default_factory=list, description="Target audience for the session")
    keyTopics: List[str] = Field(default_factory=list, description="Main topics covered in session")
    seoKeywords: List[str] = Field(default_factory=list, description="SEO keywords")

class GenerateLiveSessionResponse(BaseModel):
    """Response wrapper for live session generation."""
    status: str = "success"
    data: GeneratedLiveSessionData

