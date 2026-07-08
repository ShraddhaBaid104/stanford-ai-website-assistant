"""
Main entry point for the Stanford AI Website Assistant.

Initializes the FastAPI application and registers all API routes.

Author: Shraddha Nahata
"""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Stanford AI Website Assistant",
    description="""
A production-grade Retrieval-Augmented Generation (RAG) assistant
for answering Stanford University website queries using semantic
search, ChromaDB, OpenAI embeddings, and GPT models.
""",
    version="1.0.0",
    contact={
        "name": "Shraddha Nahata",
        "url": "https://github.com/ShraddhaBaid104/stanford-ai-website-assistant",
    },
    license_info={
        "name": "MIT License",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router)