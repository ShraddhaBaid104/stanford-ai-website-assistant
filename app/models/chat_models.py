"""
Shared domain models for the Stanford AI Website Assistant.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Citation(BaseModel):
    """
    Represents a source used to generate an answer.
    """

    title: str
    url: str
    score: Optional[float] = None


class RetrievedDocument(BaseModel):
    """
    Internal representation of a retrieved Stanford document.
    """

    id: str
    title: str
    url: str
    content: str
    score: Optional[float] = None

class ChatResponse(BaseModel):
    """
    Standard response returned by the chatbot.
    """

    answer: str

    citations: List[Citation] = Field(default_factory=list)