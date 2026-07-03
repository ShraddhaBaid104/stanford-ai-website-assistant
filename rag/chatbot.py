"""
Production Stanford Website Chatbot

Responsible for:
- Retrieving relevant Stanford documents
- Building grounded prompts
- Invoking the OpenAI chat model
- Returning the generated answer along with source URLs

Author: Shraddha Nahata
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from langchain_openai import ChatOpenAI

from config import (
    OPENAI_API_KEY,
    CHAT_MODEL,
    TEMPERATURE,
    TOP_K_RESULTS,
)

from rag.prompt_builder import PromptBuilder
from rag.retriever import StanfordRetriever


@dataclass
class ChatResponse:
    """
    Standard response returned by the chatbot.
    """

    answer: str
    sources: List[str]


class StanfordChatbot:
    """
    Production Retrieval-Augmented Generation (RAG) chatbot.
    """

    def __init__(
        self,
        k: int = TOP_K_RESULTS,
    ):

        self.retriever = StanfordRetriever(k=k)

        self.prompt_builder = PromptBuilder()

        self.llm = ChatOpenAI(
            model=CHAT_MODEL,
            temperature=TEMPERATURE,
            api_key=OPENAI_API_KEY,
        )

    def ask(
        self,
        question: str,
    ) -> ChatResponse:
        """
        Public interface for asking questions.
        """

        documents = self._retrieve_documents(question)

        messages = self._build_messages(
            question,
            documents,
        )

        answer = self._generate_answer(messages)

        sources = self._collect_sources(documents)

        return ChatResponse(
            answer=answer,
            sources=sources,
        )

    def _retrieve_documents(
        self,
        question: str,
    ):
        """
        Retrieve relevant Stanford documents.
        """

        return self.retriever.retrieve(question)

    def _build_messages(
        self,
        question,
        documents,
    ):
        """
        Build chat messages for the LLM.
        """

        return self.prompt_builder.build_messages(
            question=question,
            documents=documents,
        )

    def _generate_answer(
        self,
        messages,
    ) -> str:
        """
        Generate an answer from the language model.
        """

        try:

            response = self.llm.invoke(messages)

            return response.content

        except Exception as exc:

            raise RuntimeError(
                f"Failed to generate response: {exc}"
            ) from exc

    def _collect_sources(
        self,
        documents,
    ) -> List[str]:
        """
        Collect unique source URLs while preserving order.
        """

        seen = set()

        sources = []

        for doc in documents:

            url = doc.metadata.get("url")

            if url and url not in seen:

                seen.add(url)

                sources.append(url)

        return sources
