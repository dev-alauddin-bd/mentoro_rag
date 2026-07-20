"""
LLM and Chain Configuration
Initializes Groq LLM, HuggingFace embeddings, and LangChain components.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from huggingface_hub import login

# 🎯 os.getenv দিয়ে এনভায়রনমেন্ট ভ্যারিয়েবল রিড করা হচ্ছে
HF_TOKEN = os.getenv("HF_TOKEN")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-mpnet-base-v2")

# HuggingFace Authentication
if HF_TOKEN:
    login(token=HF_TOKEN)

# Initialize LLM
llm = ChatGroq(
    model_name=LLM_MODEL,
    temperature=LLM_TEMPERATURE,
    api_key=GROQ_API_KEY
)

# Initialize Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

# Query Rewriter Prompt
rewrite_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a multilingual query optimizer. Rewrite Banglish/Romanized Bengali queries into professional English optimized for LLM execution.

Rules:
1. Map Romanized Bengali phonetics to true semantic English based on context.
2. Preserve exact intent and constraints.
3. Do NOT answer the question — only rewrite it.
4. Output ONLY the rewritten question string. No preamble, no markdown."""),
    ("human", "{question}")
])

# Build rewriter chain
rewriter_chain = rewrite_prompt | llm | StrOutputParser()
