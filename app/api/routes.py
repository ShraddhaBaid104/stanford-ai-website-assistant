"""
API Routes

Defines the REST API endpoints for the Stanford AI Website Assistant.

Author: Shraddha Nahata
"""

from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.core.exceptions import StanfordAssistantError
from app.core.logging import logger
from app.dependencies.chat import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from fastapi.responses import StreamingResponse

router = APIRouter(
    tags=["Stanford AI Website Assistant"],
)


@router.get(
    "/",
    summary="API Root",
)
def root() -> dict[str, str]:
    """
    Root endpoint.
    """

    logger.info("Root endpoint accessed.")

    return {
        "message": "Stanford AI Website Assistant API is running."
    }


@router.get(
    "/health",
    summary="Health Check",
)
def health() -> dict[str, str]:
    """
    Health check endpoint.
    """

    logger.info("Health check requested.")

    return {
        "status": "healthy",
    }


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask the Stanford AI Assistant",
)

def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:

    logger.info("Received chat request.")

    try:

        result = chat_service.ask(
            session_id=request.session_id,
            question=request.question,
        )

        logger.info("Chat request completed successfully.")

        return ChatResponse(
            answer=result.answer,
            citations=result.citations,
        )

    except StanfordAssistantError as exc:

        logger.exception(str(exc))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    except Exception:

        logger.exception("Unexpected server error.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected server error occurred.",
        )

@router.get(
    "/chat/last-citations",
    summary="Get latest citations",
)
def last_citations(
    session_id: str,
    chat_service: ChatService = Depends(get_chat_service),
):

    logger.info(
        "Returning cached citations for session %s",
        session_id,
    )

    return {
        "citations": chat_service.get_last_citations(
            session_id
        )
    }
@router.post(
    "/chat/stream",
    summary="Stream chat response",
)
def stream_chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    generator = chat_service.stream(
        session_id=request.session_id,
        question=request.question,
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )