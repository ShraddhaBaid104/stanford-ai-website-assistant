"""
Production Conversation Summarizer

Summarizes long conversations to reduce token usage while
preserving important context.

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_openai import ChatOpenAI

from app.core.config import (
    CHAT_MODEL,
    OPENAI_API_KEY,
)

from app.core.logging import logger


class ConversationSummarizer:
    """
    Summarizes older conversation history.
    """

    SYSTEM_PROMPT = """
You summarize conversations for an AI assistant.

Rules:

1. Produce a concise summary.

2. Preserve:
   - important entities
   - previous questions
   - user goals
   - important answers

3. Do not invent information.

4. Keep the summary under 200 words.

5. Output ONLY the summary.
"""

    def __init__(self):

        logger.info("Initializing ConversationSummarizer.")

        self.llm = ChatOpenAI(
            model=CHAT_MODEL,
            temperature=0,
            api_key=OPENAI_API_KEY,
        )

        logger.info("ConversationSummarizer initialized.")

    def summarize(
        self,
        history: List[str],
    ) -> str:
        logger.info(f"History contains {len(history)} messages.")

        if len(history) <= 10:
            logger.info("Conversation too short to summarize.")
            return ""

        old_history = "\n".join(history[:-6])

        response = self.llm.invoke(
            [
                SystemMessage(
                    content=self.SYSTEM_PROMPT.strip()
                ),
                HumanMessage(content=old_history),
            ]
        )

        summary = response.content.strip()

        logger.info("Conversation summarized.")

        return summary