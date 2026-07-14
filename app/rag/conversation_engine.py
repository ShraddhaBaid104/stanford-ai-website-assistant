"""
Production Conversation Engine

Coordinates the complete conversational RAG workflow.

Responsibilities
----------------
- Conversation memory
- Query rewriting
- Conversation summarization
- Hybrid retrieval
- Prompt construction
- LLM generation
- Response validation
- Citation generation
- Citation caching
- Response caching
- Analytics
- Metrics

Author: Shraddha Nahata
"""

from __future__ import annotations

from typing import List

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

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
from app.services import MetricsService

from app.services import (
    citation_service,
    response_cache,
    semantic_cache,
    analytics_service,
)
from app.rag.guardrails.guardrail_service import GuardrailService
from app.services.evaluation_service import EvaluationService

class ConversationEngine:
    """
    Production conversational RAG engine.
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

        self.metrics = MetricsService()

        self.response_validator = ResponseValidator()

        self.guardrails = GuardrailService()

        self.evaluation = EvaluationService()

        self.llm = ChatOpenAI(
            model=CHAT_MODEL,
            temperature=TEMPERATURE,
            api_key=OPENAI_API_KEY,
        )

        logger.info(
            "ConversationEngine initialized successfully."
        )

    ####################################################################
    # STANDARD CHAT
    ####################################################################

    def chat(
            self,
            session_id: str,
            question: str,
    ) -> ChatResponse:
        """
        Execute one conversational RAG request.
        """

        self.metrics.start("total")

        try:

            # --------------------------------------------------
            # Response Cache
            # --------------------------------------------------

            cached = response_cache.get(
                session_id=session_id,
                question=question,
            )

            if cached:
                logger.info(
                    "Response cache hit."
                )

                analytics_service.record_request(
                    cached=True,
                )

                logger.info(
                    "Total request took %.2fs",
                    self.metrics.stop("total"),
                )

                return ChatResponse(**cached)
            # --------------------------------------------------
            # Guardrails (Question Validation)
            # --------------------------------------------------

            guardrail_response = self.guardrails.validate_question(
                question
            )

            if guardrail_response:
                logger.info(
                    "Question blocked by guardrails."
                )

                analytics_service.record_request(
                    cached=False,
                )

                return ChatResponse(
                    answer=guardrail_response,
                    citations=[],
                )
            # --------------------------------------------------
            # Semantic Cache
            # --------------------------------------------------

            semantic = semantic_cache.get(
                question
            )

            if semantic:
                logger.info(
                    "Semantic cache hit."
                )

                analytics_service.record_request(
                    cached=True,
                )

                citation_service.save(
                    session_id=session_id,
                    citations=semantic.citations,
                )

                logger.info(
                    "Total request took %.2fs",
                    self.metrics.stop("total"),
                )

                return semantic

            # --------------------------------------------------
            # Conversation History
            # --------------------------------------------------

            logger.info(
                "Loading conversation history."
            )

            history = self.memory_service.get_history(
                session_id
            )

            # --------------------------------------------------
            # Summarization
            # --------------------------------------------------

            logger.info(
                "Summarizing conversation."
            )

            summary = self.conversation_summarizer.summarize(
                history
            )

            # --------------------------------------------------
            # Query Rewrite
            # --------------------------------------------------

            self.metrics.start("rewrite")

            logger.info(
                "Rewriting query."
            )

            retrieval_question = self.query_rewriter.rewrite(
                question=question,
                conversation_history=history,
            )

            logger.info(
                "Rewrite took %.2fs",
                self.metrics.stop("rewrite"),
            )

            logger.info(
                "Retrieval query: %s",
                retrieval_question,
            )

            # --------------------------------------------------
            # Retrieval
            # --------------------------------------------------

            self.metrics.start("retrieval")

            logger.info(
                "Retrieving Stanford documents."
            )

            documents = self._retrieve_documents(
                retrieval_question
            )
            # --------------------------------------------------
            # Guardrails (Retrieved Context)
            # --------------------------------------------------

            guardrail_response = self.guardrails.validate_documents(
                documents
            )

            if guardrail_response:
                logger.info(
                    "Retrieval blocked by guardrails."
                )

                analytics_service.record_request(
                    cached=False,
                )

                return ChatResponse(
                    answer=guardrail_response,
                    citations=[],
                )

            logger.info(
                "Retrieval took %.2fs",
                self.metrics.stop("retrieval"),
            )

            # --------------------------------------------------
            # Prompt Construction
            # --------------------------------------------------

            logger.info(
                "Building prompt."
            )

            messages = self._build_messages(
                question=question,
                documents=documents,
                history=history,
                summary=summary,
            )

            # --------------------------------------------------
            # LLM Generation
            # --------------------------------------------------

            self.metrics.start("llm")

            logger.info(
                "Generating response."
            )

            answer = self._generate_answer(
                messages
            )

            logger.info(
                "LLM took %.2fs",
                self.metrics.stop("llm"),
            )

            # --------------------------------------------------
            # Validation
            # --------------------------------------------------

            logger.info(
                "Validating response."
            )

            answer = self.response_validator.validate(
                answer
            )

            # --------------------------------------------------
            # Save Memory
            # --------------------------------------------------

            self.memory_service.save_user_message(
                session_id,
                question,
            )

            self.memory_service.save_assistant_message(
                session_id,
                answer,
            )

            # --------------------------------------------------
            # Citations
            # --------------------------------------------------

            citations = self._build_citations(
                documents
            )

            citation_service.save(
                session_id=session_id,
                citations=citations,
            )
            logger.info(
                "Saved %d citations for session %s",
                len(citations),
                session_id,
            )

            # --------------------------------------------------
            # Response
            # --------------------------------------------------

            response = ChatResponse(
                answer=answer,
                citations=citations,
            )

            # --------------------------------------------------
            # Cache Response
            # --------------------------------------------------

            response_cache.save(
                session_id=session_id,
                question=question,
                response=response.model_dump(),
            )
            semantic_cache.save(
                question=question,
                response=response.model_dump(),
            )

            # --------------------------------------------------
            # Analytics
            # --------------------------------------------------

            analytics_service.record_request(
                cached=False,

            )
            analytics_service.record_question(
                question
            )

            total_time = self.metrics.stop("total")

            logger.info(
                "Total request took %.2fs",
                total_time,
            )

            evaluation = self.evaluation.evaluate(
                retrieval_time=self.metrics.get("retrieval"),
                llm_time=self.metrics.get("llm"),
                total_time=total_time,
                documents=documents,
                answer=answer,
                response_cache_hit=False,
                semantic_cache_hit=False,
            )

            analytics_service.record_evaluation(
                evaluation
            )

            logger.info(
                "Evaluation: %s",
                evaluation.model_dump(),
            )

            return response
        except ChatbotError:
            raise

        except Exception as exc:

            logger.exception(
                "Conversation engine failed."
            )

            raise ChatbotError(
                f"Conversation failed: {exc}"
            ) from exc

    ####################################################################
    # STREAMING CHAT
    ####################################################################
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

        self.metrics.start("stream_total")

        try:

            # --------------------------------------------------
            # Response Cache
            # --------------------------------------------------

            cached = response_cache.get(
                session_id=session_id,
                question=question,
            )

            semantic = semantic_cache.get(
                question
            )

            if semantic:
                logger.info(
                    "Streaming semantic cache hit."
                )

                analytics_service.record_request(
                    cached=True,
                )

                citation_service.save(
                    session_id=session_id,
                    citations=semantic.citations,
                )

                yield semantic.answer

                return

            if cached:
                logger.info(
                    "Streaming response cache hit."
                )

                analytics_service.record_request(
                    cached=True,
                )

                citation_service.save(
                    session_id=session_id,
                    citations=[
                        Citation(**c)
                        for c in cached["citations"]
                    ],
                )

                logger.info(
                    "Streaming request took %.2fs",
                    self.metrics.stop("stream_total"),
                )

                yield cached["answer"]

                return
            # --------------------------------------------------
            # Guardrails (Question Validation)
            # --------------------------------------------------

            guardrail_response = self.guardrails.validate_question(
                question
            )

            if guardrail_response:
                logger.info(
                    "Question blocked by guardrails."
                )

                analytics_service.record_request(
                    cached=False,
                )

                yield guardrail_response

                return
            # --------------------------------------------------
            # Conversation History
            # --------------------------------------------------

            history = self.memory_service.get_history(
                session_id
            )

            summary = self.conversation_summarizer.summarize(
                history
            )

            # --------------------------------------------------
            # Rewrite
            # --------------------------------------------------

            self.metrics.start("rewrite")

            retrieval_question = self.query_rewriter.rewrite(
                question=question,
                conversation_history=history,
            )

            logger.info(
                "Rewrite took %.2fs",
                self.metrics.stop("rewrite"),
            )

            # --------------------------------------------------
            # Retrieval
            # --------------------------------------------------

            self.metrics.start("retrieval")

            documents = self._retrieve_documents(
                retrieval_question
            )
            # --------------------------------------------------
            # Guardrails (Retrieved Context)
            # --------------------------------------------------

            guardrail_response = self.guardrails.validate_documents(
                documents
            )

            if guardrail_response:
                logger.info(
                    "Retrieval blocked by guardrails."
                )

                analytics_service.record_request(
                    cached=False,
                )

                yield guardrail_response

                return

            logger.info(
                "Retrieval took %.2fs",
                self.metrics.stop("retrieval"),
            )

            # --------------------------------------------------
            # Prompt
            # --------------------------------------------------

            messages = self._build_messages(
                question=question,
                documents=documents,
                history=history,
                summary=summary,
            )

            # --------------------------------------------------
            # Stream LLM
            # --------------------------------------------------

            self.metrics.start("llm")

            stream = self.llm.stream(
                messages
            )

            complete_answer = ""

            for chunk in stream:

                if chunk.content:
                    complete_answer += chunk.content

                    yield chunk.content

            logger.info(
                "LLM took %.2fs",
                self.metrics.stop("llm"),
            )

            # --------------------------------------------------
            # Validation
            # --------------------------------------------------

            complete_answer = self.response_validator.validate(
                complete_answer
            )

            # --------------------------------------------------
            # Memory
            # --------------------------------------------------

            self.memory_service.save_user_message(
                session_id,
                question,
            )

            self.memory_service.save_assistant_message(
                session_id,
                complete_answer,
            )

            # --------------------------------------------------
            # Citations
            # --------------------------------------------------

            citations = self._build_citations(
                documents
            )

            citation_service.save(
                session_id=session_id,
                citations=citations,
            )
            # --------------------------------------------------
            # Create Response Object
            # --------------------------------------------------

            response = ChatResponse(
                answer=complete_answer,
                citations=citations,
            )

            # --------------------------------------------------
            # Cache Response
            # --------------------------------------------------

            response_cache.save(
                session_id=session_id,
                question=question,
                response=response.model_dump(),
            )

            semantic_cache.save(
                question=question,
                response=response.model_dump(),
            )

            # --------------------------------------------------
            # Analytics
            # --------------------------------------------------

            analytics_service.record_request(
                cached=False,
            )

            analytics_service.record_question(
                question,
            )

            total_time = self.metrics.stop("stream_total")

            logger.info(
                "Streaming request took %.2fs",
                total_time,
            )

            evaluation = self.evaluation.evaluate(
                retrieval_time=self.metrics.get("retrieval"),
                llm_time=self.metrics.get("llm"),
                total_time=total_time,
                documents=documents,
                answer=complete_answer,
                response_cache_hit=False,
                semantic_cache_hit=False,
            )
            analytics_service.record_evaluation(
                evaluation
            )
            logger.info(
                "Evaluation: %s",
                evaluation.model_dump(),
            )
        except Exception as exc:

            logger.exception(
                "Streaming conversation failed."
            )

            raise ChatbotError(
                f"Streaming conversation failed: {exc}"
            ) from exc

    ####################################################################
    # RETRIEVAL
    ####################################################################

    def _retrieve_documents(
        self,
        question: str,
    ) -> List[RetrievedDocument]:
        """
        Retrieve the most relevant Stanford documents.
        """

        return self.retriever.retrieve(
            question
        )
    ####################################################################
    # PROMPT BUILDING
    ####################################################################

    def _build_messages(
        self,
        question: str,
        documents: List[RetrievedDocument],
        history: List[str],
        summary: str,
    ) -> List[BaseMessage]:
        """
        Build the prompt sent to the LLM.
        """

        return self.prompt_builder.build_messages(
            question=question,
            documents=documents,
            conversation_history=history,
            summary=summary,
        )
    ####################################################################
    # LLM GENERATION
    ####################################################################

    def _generate_answer(
        self,
        messages: List[BaseMessage],
    ) -> str:
        """
        Invoke the LLM and return the generated answer.
        """

        response = self.llm.invoke(
            messages
        )

        return str(
            response.content
        )
    ####################################################################
    # CITATION BUILDER
    ####################################################################

    @staticmethod
    def _build_citations(
            documents: List[RetrievedDocument],
    ) -> List[Citation]:
        """
        Convert retrieved documents into unique citations.
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
