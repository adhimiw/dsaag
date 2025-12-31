"""LLM factory for creating LLM instances."""

from enum import Enum
from typing import Optional

from config import get_settings
from utils.logger import get_logger
from llm.base_llm import BaseLLM
from llm.google_llm import GoogleLLM
from llm.mistral_llm import MistralLLM

logger = get_logger(__name__)


class LLMProvider(str, Enum):
    """LLM provider options."""

    MISTRAL = "mistral"
    GOOGLE = "google"


def get_llm(provider: Optional[str] = None, **kwargs) -> BaseLLM:
    """Get an LLM instance based on provider.

    Args:
        provider: LLM provider name ("mistral" or "google")
        **kwargs: Additional arguments passed to LLM constructor

    Returns:
        LLM instance
    """
    settings = get_settings()
    provider = provider or settings.primary_llm_provider

    if provider == LLMProvider.MISTRAL:
        logger.info("Creating Mistral LLM instance")
        return MistralLLM(**kwargs)
    elif provider == LLMProvider.GOOGLE:
        logger.info("Creating Google Gemini LLM instance")
        return GoogleLLM(**kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

