"""
Main entry point for the Stanford AI Website Assistant.

Initializes the FastAPI application and registers all API routes.

Author: Shraddha Nahata
"""

from fastapi import FastAPI

from app.api.routes import router
from contextlib import asynccontextmanager

from app.dependencies.chat import chat_service

@asynccontextmanager
async def lifespan(app):

    # Force initialization
    _ = chat_service

    yield


app = FastAPI(
    title="Stanford AI Website Assistant",
    lifespan=lifespan,
)

app.include_router(router)