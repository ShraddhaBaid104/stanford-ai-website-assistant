"""
Base interface for document rerankers.

Author: Shraddha Nahata
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.models import RetrievedDocument


class BaseReranker(ABC):
    """
    Interface for reranking retrieved documents.
    """

    @abstractmethod
    def rerank(
        self,
        question: str,
        documents: List[RetrievedDocument],
    ) -> List[RetrievedDocument]:
        """
        Return documents ordered by relevance.
        """
        raise NotImplementedError