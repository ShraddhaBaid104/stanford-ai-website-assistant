"""
Production Query Rewriter

Rewrites follow-up questions into standalone search queries
before document retrieval.

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.core.config import (
    CHAT_MODEL,
    OPENAI_API_KEY,
    TEMPERATURE,
)

from app.core.logging import logger


class QueryRewriter:
    """
    Uses the LLM to rewrite conversational questions into
    standalone retrieval queries.
    """

    SYSTEM_PROMPT = """
You rewrite conversational questions for document retrieval.

Rules:

1. Rewrite the user's latest question into a standalone question.

2. Preserve the original meaning.

3. Include important context from conversation history if needed.

4. Do NOT answer the question.

5. Do NOT invent facts.

6. Output ONLY the rewritten question.
"""

    def __init__(self):

        logger.info("Initializing QueryRewriter.")

        self.llm = ChatOpenAI(
            model=CHAT_MODEL,
            temperature=0,
            api_key=OPENAI_API_KEY,
        )

        logger.info("QueryRewriter initialized.")

    def rewrite(
        self,
        question: str,
        conversation_history: List[str],
    ) -> str:

        history = "\n".join(conversation_history[-10:])

        prompt = f"""
Conversation History

{history}

--------------------------------

Current Question

{question}
"""

        response = self.llm.invoke(
            [
                SystemMessage(content=self.SYSTEM_PROMPT.strip()),
                HumanMessage(content=prompt.strip()),
            ]
        )

        rewritten = response.content.strip()

        logger.info(
            "Query rewritten: '%s' -> '%s'",
            question,
            rewritten,
        )

        return rewritten