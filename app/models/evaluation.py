"""
Evaluation Models
"""

from pydantic import BaseModel


class EvaluationResult(BaseModel):

    retrieval_time: float

    llm_time: float

    total_time: float

    retrieved_documents: int

    citation_count: int

    average_retrieval_score: float

    best_retrieval_score: float

    answer_words: int

    answer_characters: int

    response_cache_hit: bool

    semantic_cache_hit: bool

    passed: bool