"""
Course Sync Service
Handles bulk syncing of courses from external Node.js/PostgreSQL backend.
"""

from typing import List, Dict, Any
from app.config.database import db_manager      
from app.validation.schemas import CourseData

class SyncService:
    """Service class for course synchronization."""

    @staticmethod
    def build_course_document(course: CourseData) -> str:
        """Build rich document text from course data."""
        return f"""Course Title: {course.title}
Course ID: {course.id}
Category: {course.category}
Price: ${course.price}
Instructor: {course.instructor}

Description:
{course.description}

This course teaches {course.category} and is priced at ${course.price}.
Students can learn {course.title} from {course.instructor}."""

    @staticmethod
    def build_metadata(course: CourseData) -> Dict[str, str]:
        """Build metadata dictionary from course data."""
        metadata = {
            "course_id": course.id,
            "category": course.category,
            "title": course.title,
            "price": str(course.price),
            "instructor": course.instructor
        }

        if course.slug:
            metadata["slug"] = course.slug
        if course.level:
            metadata["level"] = course.level
        if course.duration:
            metadata["duration"] = course.duration
        if course.tags:
            metadata["tags"] = course.tags
        if course.language:
            metadata["language"] = course.language
        if course.enrollment_count is not None:
            metadata["enrollment_count"] = str(course.enrollment_count)

        return metadata

    @staticmethod
    async def sync_courses(courses: List[CourseData]) -> Dict[str, Any]:
        """Bulk sync courses to ChromaDB."""
        results = []
        success_count = 0
        fail_count = 0

        for course in courses:
            try:
                document = SyncService.build_course_document(course)
                metadata = SyncService.build_metadata(course)

                db_manager.course_contents_store.add_texts(
                    texts=[document],
                    metadatas=[metadata]
                )

                results.append({
                    "course_id": course.id,
                    "title": course.title,
                    "status": "success",
                    "metadata_fields": list(metadata.keys())
                })
                success_count += 1

            except Exception as e:
                results.append({
                    "course_id": course.id,
                    "title": course.title,
                    "status": "failed",
                    "error": str(e)
                })
                fail_count += 1

        return {
            "status": "success" if fail_count == 0 else "partial",
            "total_processed": len(courses),
            "successful": success_count,
            "failed": fail_count,
            "details": results
        }
