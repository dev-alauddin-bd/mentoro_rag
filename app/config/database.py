"""
Mentoro RAG API - Database Manager
Handles connection initialization and lifecycle checks for ChromaDB Cloud.
"""
import os
import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from app.config.llm import embeddings  

load_dotenv()  # Load environment variables from .env file

class ChromaDBManager:
    def __init__(self):
        self.client = None
        self.platform_info_store = None
        self.course_contents_store = None
        self.student_memories_store = None

    def connect(self):
        """Initializes and tests connection to ChromaDB Cloud."""
        print("\n--- Connecting to Mentoro Vector Infrastructure (HuggingFace Embeddings) ---")
        
        api_key = os.environ.get('CHROMA_API_KEY')
        tenant_id = os.environ.get('CHROMA_TENANT_ID')
        db_name = os.environ.get('CHROMA_DATABASE_NAME')

        if api_key and tenant_id and db_name:
            try:
                # Initialize Cloud Client
                self.client = chromadb.CloudClient(
                    tenant=tenant_id,
                    database=db_name,
                    api_key=api_key
                )
                
                # Test connection with a heartbeat
                self.client.heartbeat()
                print("✅ Success: Connected to ChromaDB Cloud successfully!")
                
                # 🎯 সব কালেকশনে HuggingFace এম্বেডিং সেট করা হলো
                self.platform_info_store = Chroma(
                    client=self.client,
                    collection_name="platform_info",
                    embedding_function=embeddings
                )
                
                self.course_contents_store = Chroma(
                    client=self.client,
                    collection_name="course_contents",
                    embedding_function=embeddings
                )
                
                self.student_memories_store = Chroma(
                    client=self.client,
                    collection_name="student_memories",
                    embedding_function=embeddings
                )
                print("📦 All 3 Vector Stores (Platform, Courses, Student Memories) Loaded Successfully.")
                
            except Exception as e:
                print(f"❌ Error: Failed to connect to ChromaDB Cloud. Details: {e}")
                self.client = None
                self.platform_info_store = None
                self.course_contents_store = None
                self.student_memories_store = None
        else:
            print("❌ Error: Missing required environment variables (CHROMA_API_KEY, CHROMA_TENANT_ID, or CHROMA_DATABASE_NAME).")
            
        print("--------------------------------------------------\n")

# Global singleton instance to share across your FastAPI app
db_manager = ChromaDBManager()
