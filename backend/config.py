"""
Config file for Firecrawl AI Search.
Loads environment variables from .env file.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ====================== SERVER CONFIG ======================
PORT: int = int(os.getenv("PORT", "5000"))

# ====================== FIRECRAWL ======================
FIRECRAWL_API_KEY: str | None = os.getenv("FIRECRAWL_API_KEY")

# ====================== AI / LLM ======================
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o")
FREELLM_API_KEY: str = os.getenv("FREELLM_API_KEY", "")
FREELLM_BASE_URL: str = os.getenv("FREELLM_BASE_URL", "http://localhost:3001/v1")
