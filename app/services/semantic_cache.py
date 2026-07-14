"""
Semantic Response Cache

Stores embeddings of previous questions and reuses answers
for semantically similar future questions.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from langchain_openai import OpenAIEmbeddings

from app.core.config import OPENAI_API_KEY
from app.models import ChatResponse


class SemanticCache:

    def __init__(self):

        self.embedder = OpenAIEmbeddings(
            api_key=OPENAI_API_KEY,
            model="text-embedding-3-small",
        )

        self.entries = []

        self.threshold = 0.85

    def _cosine_similarity(
        self,
        a,
        b,
    ):

        a = np.array(a)
        b = np.array(b)

        return float(
            np.dot(a, b)
            /
            (
                np.linalg.norm(a)
                *
                np.linalg.norm(b)
            )
        )

    def get(
        self,
        question: str,
    ) -> Optional[ChatResponse]:

        if not self.entries:
            return None

        embedding = self.embedder.embed_query(
            question
        )

        best_score = 0
        best_response = None

        for item in self.entries:

            score = self._cosine_similarity(
                embedding,
                item["embedding"],
            )

            if score > best_score:

                best_score = score
                best_response = item["response"]

        if best_score >= self.threshold:

            return ChatResponse(
                **best_response
            )

        return None

    def save(
        self,
        question: str,
        response: dict,
    ):

        embedding = self.embedder.embed_query(
            question
        )

        self.entries.append(
            {
                "embedding": embedding,
                "response": response,
            }
        )


# Singleton instance
semantic_cache = SemanticCache()