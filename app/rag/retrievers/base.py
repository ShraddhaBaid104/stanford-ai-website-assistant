"""
Abstract base class for all retrievers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.models import RetrievedDocument


class BaseRetriever(ABC):
    """
    Interface implemented by all retrievers.
    """

    @abstractmethod
    def retrieve(
        self,
        question: str,
    ) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents.
        """
        raise NotImplementedError