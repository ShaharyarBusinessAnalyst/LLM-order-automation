"""
Configuration loader.
Reads environment variables from .env file.
All API keys and config values go here — never hardcoded.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


def get_openai_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "OPENAI_API_KEY not set. Copy .env.example to .env and add your key."
        )
    return key


def get_pinecone_key() -> str:
    key = os.getenv("PINECONE_API_KEY", "")
    if not key:
        raise EnvironmentError(
            "PINECONE_API_KEY not set. Copy .env.example to .env and add your key."
        )
    return key


def get_pinecone_index() -> str:
    return os.getenv("PINECONE_INDEX_NAME", "order-automation")


def get_pinecone_host() -> str:
    return os.getenv("PINECONE_HOST", "")


# Model config
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_CHAT_MODEL = "gpt-4o-mini"
PINECONE_DIMENSION = 1536       # text-embedding-3-small output dimension
PINECONE_METRIC = "cosine"

# Pipeline config
SIMILARITY_THRESHOLD = 0.75     # Below this → flag for human review
TOP_K_RESULTS = 3               # Number of SKU candidates to retrieve
MAX_RETRIES = 3                 # OpenAI call retries
