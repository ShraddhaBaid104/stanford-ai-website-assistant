"""
Production Conversation Engine

Responsible for:
- Loading conversation history
- Retrieving relevant Stanford documents
- Building prompts
- Invoking the language model
- Validating responses
- Persisting conversation memory
- Returning the final response

Author: Shraddha Nahata
"""

from __future__ import annotations
from app.services import citation_service

from typing import List

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
import time

from app.services.analytics_service import AnalyticsService

from app.core.config import (
    CHAT_MODEL,
    OPENAI_API_KEY,
    TEMPERATURE,
    TOP_K_RESULTS,
)

from app.core.exceptions import ChatbotError
from app.core.logging import logger

from app.models import (
    ChatResponse,
    Citation,
    RetrievedDocument,
)

from app.rag.conversation_summarizer import ConversationSummarizer
from app.rag.prompt_builder import PromptBuilder
from app.rag.query_rewriter import QueryRewriter
from app.rag.response_validator import ResponseValidator
from app.rag.retrievers.base import BaseRetriever
from app.rag.retrievers.hybrid_retriever import HybridRetriever
from app.services.memory_service import MemoryService


class ConversationEngine:
    """
    Coordinates the conversational RAG workflow.
    """

    def __init__(
        self,
        k: int = TOP_K_RESULTS,
    ):
            logger.info("Initializing ConversationEngine.")

            self.retriever: BaseRetriever = HybridRetriever(k=k)

            self.query_rewriter = QueryRewriter()

            self.conversation_summarizer = ConversationSummarizer()

            self.prompt_builder = PromptBuilder()

            self.memory_service = MemoryService()

            self.analytics = AnalyticsService()  # ← Add this

            self.response_validator = ResponseValidator()

            self.llm = ChatOpenAI(
                model=CHAT_MODEL,
                temperature=TEMPERATURE,
                api_key=OPENAI_API_KEY,
            )

            logger.info("ConversationEngine initialized successfully.")

    def chat(
        self,
        session_id: str,
        question: str,
    ) -> ChatResponse:
        """
        Execute one conversational RAG request.
        """

        try:

            logger.info("Loading conversation history.")

            history = self.memory_service.get_history(
                session_id
            )

            logger.info("Summarizing conversation.")

            summary = self.conversation_summarizer.summarize(
                history
            )

            logger.info("Rewriting query.")

            retrieval_question = self.query_rewriter.rewrite(
                question=question,
                conversation_history=history,
            )

            logger.info(
                "Retrieval query: %s",
                retrieval_question,
            )

            logger.info("Retrieving Stanford documents.")

            documents = self._retrieve_documents(
                retrieval_question
            )

            logger.info("Building prompt.")

            messages = self._build_messages(
                question,
                documents,
                history,
                summary,
            )

            logger.info("Generating response from OpenAI.")

            answer = self._generate_answer(
                messages
            )

            logger.info("Validating response.")

            answer = self.response_validator.validate(
                answer
            )

            logger.info("Saving conversation history.")

            self.memory_service.save_user_message(
                session_id,
                question,
            )

            self.memory_service.save_assistant_message(
                session_id,
                answer,
            )

            citations = self._build_citations(documents)

            citation_service.save(
                session_id,
                citations,
            )

            return ChatResponse(
                answer=answer,
                citations=citations,
            )


        except ChatbotError:
            raise

        except Exception as exc:

            logger.exception(
                "Conversation engine failed."
            )

            raise ChatbotError(
                f"Conversation failed: {exc}"
            ) from exc

    def _retrieve_documents(
        self,
        question: str,
    ) -> List[RetrievedDocument]:

        return self.retriever.retrieve(
            question
        )

    def _build_messages(
        self,
        question: str,
        documents: List[RetrievedDocument],
        history: List[str],
        summary: str,
    ) -> List[BaseMessage]:

        return self.prompt_builder.build_messages(
            question=question,
            documents=documents,
            conversation_history=history,
            summary=summary,
        )

    def _generate_answer(
        self,
        messages: List[BaseMessage],
    ) -> str:

        response = self.llm.invoke(
            messages
        )

        return str(
            response.content
        )

    @staticmethod
    def _build_citations(
        documents: List[RetrievedDocument],
    ) -> List[Citation]:
        """
        Build a unique list of citations.
        """

        citations: List[Citation] = []

        seen_urls: set[str] = set()

        for document in documents:

            if not document.url:
                continue

            if document.url in seen_urls:
                continue

            seen_urls.add(
                document.url
            )

            citations.append(
                Citation(
                    title=document.title,
                    url=document.url,
                    score=document.score,
                )
            )

        return citations

    def stream_chat(
        self,
        session_id: str,
        question: str,
    ):
        """
        Stream one conversational RAG request.
        """

        logger.info(
            "Streaming chat response."
        )

        history = self.memory_service.get_history(
            session_id
        )

        summary = self.conversation_summarizer.summarize(
            history
        )

        retrieval_question = self.query_rewriter.rewrite(
            question=question,
            conversation_history=history,
        )

        documents = self._retrieve_documents(
            retrieval_question
        )

        messages = self._build_messages(
            question,
            documents,
            history,
            summary,
        )

        response = self.llm.stream(
            messages
        )

        complete_answer = ""

        for chunk in response:

            if chunk.content:

                complete_answer += chunk.content

                yield chunk.content

        complete_answer = self.response_validator.validate(
            complete_answer
        )

        self.memory_service.save_user_message(
            session_id,
            question,
        )

        self.memory_service.save_assistant_message(
            session_id,
            complete_answer,
        )
        citations = self._build_citations(documents)

        citation_service.save(
            session_id=session_id,
            citations=citations,
        )