"""
API request and response schemas.

Author: Shraddha Nahata
"""

from pydantic import BaseModel, Field

from app.models import Citation


class ChatRequest(BaseModel):
    """
    Chat request payload.
    """

    session_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    """
    Chat response returned by the API.
    """

    answer: str

    citations: list[Citation] = Field(default_factory=list)