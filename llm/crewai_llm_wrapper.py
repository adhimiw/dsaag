"""CrewAI LLM wrapper for Mistral and Google LLM providers."""

from typing import Any, Optional

from utils.logger import get_logger
from .base_llm import BaseLLM

logger = get_logger(__name__)


class CrewAIMistralLLM:
    """CrewAI-compatible LLM wrapper for Mistral."""

    def __init__(self, mistral_llm: BaseLLM):
        """Initialize CrewAI LLM wrapper with Mistral LLM.

        Args:
            mistral_llm: Mistral LLM instance
        """
        self.mistral_llm = mistral_llm
        # Store attributes that CrewAI might check
        # Prefix with 'mistral/' to ensure LiteLLM recognizes the provider
        model_name = mistral_llm.model if hasattr(mistral_llm, "model") else "mistral-large-latest"
        if not model_name.startswith("mistral/"):
            self.model = f"mistral/{model_name}"
        else:
            self.model = model_name
            
        self.api_key = mistral_llm.api_key if hasattr(mistral_llm, "api_key") else None
        logger.info(f"Created CrewAI Mistral LLM wrapper with model: {self.model}")

    def call(self, messages: list, **kwargs: Any) -> str:
        """Call Mistral LLM through CrewAI interface.

        Args:
            messages: List of messages
            **kwargs: Additional arguments

        Returns:
            LLM response
        """
        # Extract system prompt and user prompt from messages
        system_prompt = None
        user_prompt = None

        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content")
            elif msg.get("role") == "user":
                user_prompt = msg.get("content")

        if not user_prompt:
            # Fallback: combine all messages
            user_prompt = "\n".join([msg.get("content", "") for msg in messages])

        return self.mistral_llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            **kwargs
        )


class CrewAIGoogleLLM:
    """CrewAI-compatible LLM wrapper for Google Gemini."""

    def __init__(self, google_llm: BaseLLM):
        """Initialize CrewAI LLM wrapper with Google LLM.

        Args:
            google_llm: Google LLM instance
        """
        self.google_llm = google_llm
        # Store attributes that CrewAI might check
        self.model = google_llm.model if hasattr(google_llm, "model") else "gemini-2.5-pro"
        self.api_key = google_llm.api_key if hasattr(google_llm, "api_key") else None
        logger.info("Created CrewAI Google Gemini LLM wrapper")

    def call(self, messages: list, **kwargs: Any) -> str:
        """Call Google LLM through CrewAI interface.

        Args:
            messages: List of messages
            **kwargs: Additional arguments

        Returns:
            LLM response
        """
        # Extract system prompt and user prompt from messages
        system_prompt = None
        user_prompt = None

        for msg in messages:
            if msg.get("role") == "system":
                system_prompt = msg.get("content")
            elif msg.get("role") == "user":
                user_prompt = msg.get("content")

        if not user_prompt:
            # Fallback: combine all messages
            user_prompt = "\n".join([msg.get("content", "") for msg in messages])

        return self.google_llm.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            **kwargs
        )

