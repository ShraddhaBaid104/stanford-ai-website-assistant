"""
Custom exception hierarchy for the Stanford AI Website Assistant.

Defines application-specific exceptions to provide meaningful error
handling across the RAG pipeline and FastAPI application.

Author: Shraddha Nahata
"""


class StanfordAssistantError(Exception):
    """
    Base exception for the Stanford AI Website Assistant.
    """

    pass


class ConfigurationError(StanfordAssistantError):
    """
    Raised when the application configuration is invalid.
    """

    pass


class RetrieverError(StanfordAssistantError):
    """
    Raised when document retrieval from the vector store fails.
    """

    pass


class PromptBuilderError(StanfordAssistantError):
    """
    Raised when prompt construction fails.
    """

    pass


class ChatbotError(StanfordAssistantError):
    """
    Raised when the language model fails to generate a response.
    """

    pass


class EmbeddingError(StanfordAssistantError):
    """
    Raised when embedding generation fails.
    """

    pass


class VectorStoreError(StanfordAssistantError):
    """
    Raised when the vector store cannot be accessed.
    """

    pass


class ValidationError(StanfordAssistantError):
    """
    Raised when user input validation fails.
    """

    pass