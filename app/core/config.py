"""
Global configuration for the Stanford AI Website Assistant.

This file centralizes all configurable values used across the project.
"""

from pathlib import Path
import os

from dotenv import load_dotenv

# --------------------------------------------------
# Load Environment Variables
# --------------------------------------------------

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY not found. Please set it in your .env file."
    )

# --------------------------------------------------
# Project Root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# --------------------------------------------------
# Data Directories
# --------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"
# --------------------------------------------------
# ChromaDB
# --------------------------------------------------

CHROMA_DB_DIR = Path(
    os.getenv(
        "CHROMA_DB_PATH",
        str(VECTORSTORE_DIR / "chroma_db"),
    )
)
CHROMA_COLLECTION_NAME = "stanford_docs"

# --------------------------------------------------
# Data Files
# --------------------------------------------------

RAW_PAGES_FILE = RAW_DATA_DIR / "stanford_pages.json"

CLEANED_DOCUMENTS_FILE = PROCESSED_DATA_DIR / "cleaned_documents.json"

CHUNKED_DOCUMENTS_FILE = PROCESSED_DATA_DIR / "chunked_documents.json"

# --------------------------------------------------
# Crawl Settings
# --------------------------------------------------

START_URL = "https://www.stanford.edu"

MAX_CRAWL_DEPTH = 2

CRAWL_DELAY = 1.0

REQUEST_TIMEOUT = 30000  # milliseconds

# --------------------------------------------------
# Stanford Domain
# --------------------------------------------------

ALLOWED_DOMAINS = [
    "stanford.edu",
    "www.stanford.edu",
    "admission.stanford.edu",
    "news.stanford.edu",
    "facts.stanford.edu",
    "library.stanford.edu",
    "parents.stanford.edu",
    "alumni.stanford.edu",
    "undergrad.stanford.edu",
    "bulletin.stanford.edu",
    "doresearch.stanford.edu",
]
DOCUMENT_ID_PREFIX = "stanford"

# --------------------------------------------------
# Chunking
# --------------------------------------------------

CHUNK_SIZE = 1000

CHUNK_OVERLAP = 200

# --------------------------------------------------
# Embeddings
# --------------------------------------------------

EMBEDDING_MODEL = "text-embedding-3-small"

# --------------------------------------------------
# Retrieval (Future Use)
# --------------------------------------------------

TOP_K_RESULTS = 5

# --------------------------------------------------
# LLM (Future Use)
# --------------------------------------------------

CHAT_MODEL = "gpt-4.1-mini"

TEMPERATURE = 0.0
# --------------------------------------------------
# Redis Configuration
# --------------------------------------------------

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

REDIS_DB = int(os.getenv("REDIS_DB", 0))

REDIS_TTL_SECONDS = int(os.getenv("REDIS_TTL_SECONDS", 3600))