"""Configuration for the summarization service."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env", override=False)


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.getenv(name)
    return value if value not in (None, "") else default


class SummarizerConfig(BaseModel):
    """Configuration loaded from environment variables and optional .env file."""

    model_config = ConfigDict(extra="ignore")

    llm_provider: str = Field(
        default_factory=lambda: _env(
            "LLM_PROVIDER",
            "openrouter" if _env("OPENROUTER_API_KEY") else "openai",
        ),
        description="LLM provider: openrouter, openai, anthropic, etc.",
    )
    llm_model: str = Field(
        default_factory=lambda: _env("LLM_MODEL", "openai/gpt-oss-20b:free"),
        description="Model name (e.g., 'openai/gpt-oss-20b:free', 'gpt-4o-mini')",
    )
    llm_api_key: Optional[str] = Field(
        default_factory=lambda: (
            _env("SUMMARIZER_LLM_API_KEY")
            or _env("OPENROUTER_API_KEY")
            or _env("OPENAI_API_KEY")
            or _env("ANTHROPIC_API_KEY")
            or _env("API_KEY")
        ),
        description="API key loaded from .env or environment variables",
    )

    max_summary_length: int = Field(
        default=400,
        description="Maximum words in summary",
    )
    min_summary_length: int = Field(
        default=200,
        description="Minimum words in summary",
    )
    temperature: float = Field(
        default=0.3,
        description="LLM temperature (lower = more deterministic)",
    )

    extract_sources: bool = Field(
        default=True,
        description="Whether to extract source URLs from summary",
    )
    min_sources: int = Field(
        default=1,
        description="Minimum number of sources required",
    )

    retry_on_failure: bool = Field(
        default=True,
        description="Whether to retry on LLM failures",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts",
    )

    @classmethod
    def from_env(cls) -> "SummarizerConfig":
        return cls()
