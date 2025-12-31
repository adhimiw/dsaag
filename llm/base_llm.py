"""Base LLM interface for all LLM providers."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """Generate a text response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific arguments

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream a text response from the LLM.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific arguments

        Yields:
            Text chunks as they are generated
        """
        pass

    @abstractmethod
    def embed(self, text: str | List[str]) -> List[List[float]]:
        """Generate embeddings for text.

        Args:
            text: Single text string or list of text strings

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    def create_agent(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        **kwargs: Any
    ) -> Any:
        """Create an agent instance using this LLM provider.

        Args:
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
            tools: Optional list of tools for the agent
            **kwargs: Additional provider-specific arguments

        Returns:
            Agent instance
        """
        pass

    def supports_mcp_natively(self) -> bool:
        """Check if this LLM provider supports MCP natively.

        Returns:
            True if native MCP support is available
        """
        return False

    def supports_visual_analysis(self) -> bool:
        """Check if this LLM provider supports visual analysis.

        Returns:
            True if visual analysis is supported
        """
        return False

