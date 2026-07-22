"""
Generation Service
Handles course content and live session metadata generation using Groq LLM.
"""

from app.config.llm import llm
from app.validation.schemas import (
    GeneratedCourseContentData,
    GeneratedLiveSessionData,
)


class GenerationService:
    """Service class for AI-driven content generation tasks."""

    @staticmethod
    async def generate_course_content(topic: str) -> GeneratedCourseContentData:
        """
        Generates structured course metadata including title, descriptions, outcomes,
        prerequisites, SEO attributes, and thumbnail prompt based on the provided topic.
        """
        prompt = f"""You are an expert online course creator and instructional designer.
Generate complete and realistic online course metadata for the given topic.

Topic: {topic}

Provide detailed, high-quality, professional attributes for this course."""

        structured_llm = llm.with_structured_output(GeneratedCourseContentData)
        result = await structured_llm.ainvoke(prompt)
        return result

    @staticmethod
    async def generate_live_session(title: str) -> GeneratedLiveSessionData:
        """
        Generates structured live session details including full description, key topics,
        target audience, learning outcomes, and SEO keywords based on session title.
        """
        prompt = f"""You are an expert workshop organizer and educator.
Generate comprehensive and engaging live session details for the given session title.

Session Title: {title}

Provide detailed, engaging, and professional details for this live session."""

        structured_llm = llm.with_structured_output(GeneratedLiveSessionData)
        result = await structured_llm.ainvoke(prompt)
        return result
