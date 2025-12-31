"""Mistral AI LLM integration with native MCP support."""

from typing import Any, AsyncIterator, List, Optional

from mistralai import Mistral

from config import get_settings
from utils.logger import get_logger
from .base_llm import BaseLLM

logger = get_logger(__name__)


class MistralLLM(BaseLLM):
    """Mistral AI LLM provider with native MCP support and Agents API."""

    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-large-latest"):
        """Initialize Mistral LLM.

        Args:
            api_key: Mistral API key (defaults to settings)
            model: Model name (mistral-large-latest, mistral-medium-latest, etc.)
        """
        settings = get_settings()
        self.api_key = api_key or settings.mistral_api_key
        if self.api_key:
            self.api_key = self.api_key.strip()
        self.model = model
        self.client = Mistral(api_key=self.api_key)
        logger.info(f"Initialized Mistral LLM with model: {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """Generate a text response using Mistral API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Returns:
            Generated text response
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            # Handle response structure - may vary by SDK version
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            elif hasattr(response, 'message'):
                return response.message.content
            else:
                return str(response)
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream a text response using Mistral API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Yields:
            Text chunks as they are generated
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.client.chat.stream(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            async for chunk in stream:
                # Handle different response structures
                if hasattr(chunk, 'choices') and chunk.choices:
                    if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                elif hasattr(chunk, 'delta') and chunk.delta.content:
                    yield chunk.delta.content
                elif hasattr(chunk, 'content'):
                    yield chunk.content
        except Exception as e:
            logger.error(f"Mistral streaming error: {e}")
            raise

    def embed(self, text: str | List[str]) -> List[List[float]]:
        """Generate embeddings using Mistral API.

        Args:
            text: Single text string or list of text strings

        Returns:
            List of embedding vectors
        """
        texts = [text] if isinstance(text, str) else text
        try:
            response = self.client.embeddings.create(
                model="mistral-embed",
                inputs=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Mistral embedding error: {e}")
            raise

    def create_agent(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        **kwargs: Any
    ) -> dict:
        """Create an agent configuration for CrewAI compatibility.

        Note: Mistral's Agents API may require a different SDK version or API access.
        For now, we return a configuration dict that can be used with CrewAI.

        Args:
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
            tools: Optional list of tools (MCP tools will be exposed natively when supported)
            **kwargs: Additional arguments

        Returns:
            Agent configuration dict for CrewAI
        """
        # Build agent instructions from role, goal, and backstory
        instructions = f"""Role: {role}
Goal: {goal}
Backstory: {backstory}"""

        # Note: Mistral's native Agents API and MCP support may require
        # additional SDK features or API access. For Phase 1, we use
        # the standard chat API and return a config for CrewAI integration.
        
        logger.info(f"Created agent configuration for: {role}")
        return {
            "role": role,
            "goal": goal,
            "backstory": backstory,
            "tools": tools or [],
            "llm": self.client,
            "instructions": instructions,
            **kwargs
        }

    def supports_mcp_natively(self) -> bool:
        """Mistral supports MCP natively."""
        return True

    def supports_visual_analysis(self) -> bool:
        """Mistral supports vision models but Gemini is preferred for visual analysis."""
        return False

