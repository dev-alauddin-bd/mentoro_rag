"""
RAG (Retrieval-Augmented Generation) Service
Handles query optimization, intent classification, context retrieval, and response generation.
"""

from typing import List, Optional
from app.config.llm import llm, rewriter_chain
from app.config.database import db_manager 


class RAGService:
    """Service class for RAG operations."""

    @staticmethod
    async def optimize_query(question: str) -> str:
        """Rewrite Banglish/grammar into professional English."""
        return rewriter_chain.invoke({"question": question})

    @staticmethod
    async def predict_intent(optimized_query: str) -> str:
        """Dynamically detect if the query is a greeting/chitchat or a data search."""
        intent_prompt = f"""Analyze the user's input and classify its primary intent.
        
        Respond with exactly ONE word:
        - "GREETING" if the input is a simple greeting, chitchat, thank you, hello, goodbye, or casual pleasantry.
        - "SEARCH" if the user is asking a specific question, seeking information about courses, pricing, platform features, or student data.

        Input: {optimized_query}
        Intent:"""
        
        response = llm.invoke(intent_prompt)
        return response.content.strip().upper()

    @staticmethod
    async def retrieve_context(
        optimized_query: str,
        course_id: Optional[str] = None,
        student_id: Optional[str] = None
    ) -> List[str]:
        """Retrieve relevant documents from ChromaDB dynamically based on intent."""
        retrieved_docs = []

        # 🎯 ডাইনামিক চেকপোস্ট: গ্রীটিংস বা চিটচ্যাট হলে সরাসরি খালি লিস্ট রিটার্ন করবে
        intent = await RAGService.predict_intent(optimized_query)
        if "GREETING" in intent:
            print(f"🤖 LLM detected intent: {intent}. Skipping ChromaDB search.")
            return retrieved_docs

        if not db_manager.client:
            print("⚠️ Warning: ChromaDB Cloud is not connected!")
            return retrieved_docs

        # Search specific course
        if course_id and db_manager.course_contents_store:
            docs = db_manager.course_contents_store.similarity_search(
                query=optimized_query, k=2,
                filter={"course_id": course_id}
            )
            retrieved_docs.extend([d.page_content for d in docs])

        # Search student memories
        if student_id and db_manager.student_memories_store:
            docs = db_manager.student_memories_store.similarity_search(
                query=optimized_query, k=1,
                filter={"student_id": student_id}
            )
            retrieved_docs.extend([d.page_content for d in docs])

        # Search all courses (no filter)
        if not course_id and not student_id and not retrieved_docs and db_manager.course_contents_store:
            docs = db_manager.course_contents_store.similarity_search(
                query=optimized_query, k=5
            )
            retrieved_docs.extend([d.page_content for d in docs])

        # Fallback to platform info
        if not retrieved_docs and db_manager.platform_info_store:
            docs = db_manager.platform_info_store.similarity_search(
                query=optimized_query, k=2
            )
            retrieved_docs.extend([d.page_content for d in docs])

        return retrieved_docs

    @staticmethod
    async def generate_response(optimized_query: str, context: List[str]) -> str:
        """Generate AI response using RAG prompt."""
        context_text = "\n\n---\n\n".join(context) if context else "No relevant context found."

        final_prompt = f"""You are "Mentoro AI" — the official AI Assistant for the Mentoro LMS platform.

## WHO YOU ARE
- Name: Mentoro AI
- Role: Dedicated LMS AI Assistant
- Purpose: Help students, instructors, and visitors with course-related queries

## WHAT YOU CAN DO
1. **Course Information**: List available courses, describe course content, pricing, duration, instructor details
2. **Platform Guidance**: Explain enrollment process, refund policy, platform features, FAQ
3. **Student Support**: Retrieve student-specific notes, memories, progress (when student_id provided)
4. **Course-Specific Help**: Answer questions about specific course content (when course_id provided)
5. **Multilingual Support**: Understand Banglish (Romanized Bengali) and respond in clear English

## WHAT YOU CANNOT DO
- Access external websites or real-time internet data
- Modify, delete, or change any course content or user data
- Provide personal opinions or recommendations outside the platform context
- Discuss topics unrelated to the Mentoro LMS platform

## HALLUCINATION PREVENTION RULES
1. **Context-Only Answers**: Base your answer STRICTLY on the provided Context below
2. **No Guessing**: If the Context does not contain the answer, clearly state: "I don\'t have that information in my current context."
3. **No Fabrication**: Never invent course names, prices, instructors, or features that are not in the Context
4. **Safe Fallback**: If context is insufficient, you may provide general LMS knowledge but MUST preface with: "Based on general knowledge:"
5. **Accuracy First**: If you are uncertain about any detail, admit uncertainty rather than guessing

## SECURITY & ETHICAL CONSTRAINTS
1. **No Data Leakage**: Never reveal other students\' personal information, notes, or memories
2. **No Sensitive Info**: Do not share API keys, database credentials, or internal system details
3. **No Harmful Content**: Refuse to generate harmful, illegal, or unethical content
4. **Privacy Protection**: Respect student privacy; only access data when proper student_id is provided
5. **No System Manipulation**: Never provide instructions to bypass security, hack, or manipulate the platform
6. **Professional Tone**: Maintain respectful, helpful, and educational tone at all times

## RESPONSE FORMAT
- Be concise but complete
- Use bullet points for lists when appropriate
- Include relevant course IDs, prices, or instructor names when available in Context
- If answering in English, use simple and clear language

---

Context:
{context_text}

Question: {optimized_query}
Answer:"""

        response = llm.invoke(final_prompt)
        return response.content
