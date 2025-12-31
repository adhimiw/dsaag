"""Google Gemini LLM integration with visual analysis capabilities."""

from typing import Any, AsyncIterator, List, Optional

try:
    # Try new google.genai package first
    import google.genai as genai
    USE_NEW_API = True
except ImportError:
    # Fallback to deprecated google.generativeai
    import google.generativeai as genai
    USE_NEW_API = False
    import warnings
    warnings.warn(
        "google.generativeai is deprecated. Please install google-genai: pip install google-genai",
        FutureWarning
    )

from config import get_settings
from utils.logger import get_logger
from .base_llm import BaseLLM

logger = get_logger(__name__)


class GoogleLLM(BaseLLM):
    """Google Gemini LLM provider with code execution and visual thinking."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-pro",
        enable_code_execution: bool = True,
    ):
        """Initialize Google Gemini LLM.

        Args:
            api_key: Google API key (defaults to settings)
            model: Model name (gemini-2.5-pro, gemini-2.5-flash, gemini-1.5-pro, etc.)
            enable_code_execution: Enable Gemini's code execution tool
        """
        settings = get_settings()
        self.api_key = api_key or settings.google_api_key
        if not self.api_key:
            raise ValueError("Google API key is required for Gemini LLM")
        self.model = model
        self.enable_code_execution = enable_code_execution
        self.use_new_api = USE_NEW_API

        if USE_NEW_API:
            # New google.genai API
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"Initialized Google Gemini LLM with model: {model} (using google.genai)")
        else:
            # Deprecated google.generativeai API
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
            logger.info(f"Initialized Google Gemini LLM with model: {model} (using deprecated google.generativeai)")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """Generate a text response using Gemini API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments (tools, etc.)

        Returns:
            Generated text response
        """
        generation_config = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens

        # Build system instruction if provided
        if system_prompt:
            generation_config["system_instruction"] = system_prompt

        # Enable code execution if requested
        tools = kwargs.get("tools", [])
        if self.enable_code_execution and "code_execution" not in [t.get("name") for t in tools]:
            # Note: Code execution is enabled via the model configuration
            pass

        try:
            if USE_NEW_API:
                # New API structure
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=generation_config,
                    tools=tools if tools else None,
                    **{k: v for k, v in kwargs.items() if k != "tools"}
                )
                return response.text
            else:
                # Deprecated API
                response = self.client.generate_content(
                    prompt,
                    generation_config=generation_config,
                    tools=tools if tools else None,
                    **{k: v for k, v in kwargs.items() if k != "tools"}
                )
                return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Stream a text response using Gemini API.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments

        Yields:
            Text chunks as they are generated
        """
        generation_config = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens

        if system_prompt:
            generation_config["system_instruction"] = system_prompt

        try:
            if USE_NEW_API:
                # New API structure
                response = self.client.models.generate_content_stream(
                    model=self.model,
                    contents=prompt,
                    config=generation_config,
                    **kwargs
                )
                async for chunk in response:
                    if hasattr(chunk, 'text') and chunk.text:
                        yield chunk.text
            else:
                # Deprecated API
                response = self.client.generate_content(
                    prompt,
                    generation_config=generation_config,
                    stream=True,
                    **kwargs
                )
                async for chunk in response:
                    if chunk.text:
                        yield chunk.text
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise

    def embed(self, text: str | List[str]) -> List[List[float]]:
        """Generate embeddings using Gemini API.

        Args:
            text: Single text string or list of text strings

        Returns:
            List of embedding vectors
        """
        texts = [text] if isinstance(text, str) else text
        try:
            if USE_NEW_API:
                # New API structure
                response = self.client.models.embed_content(
                    model="text-embedding-004",
                    contents=texts,
                    # task_type="retrieval_document"  # Not supported in this SDK version as direct arg
                )
                return [item.embedding for item in response.embeddings]
            else:
                # Deprecated API
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=texts,
                    task_type="retrieval_document"
                )
                return result["embeddings"]
        except Exception as e:
            logger.error(f"Gemini embedding error: {e}")
            raise

    def create_agent(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        **kwargs: Any
    ) -> Any:
        """Create an agent using Gemini (wrapped for CrewAI compatibility).

        Args:
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
            tools: Optional list of tools (will be wrapped as function calls)
            **kwargs: Additional arguments

        Returns:
            Agent configuration dict for CrewAI
        """
        # Gemini doesn't have a native Agents API like Mistral
        # Return configuration that can be used with CrewAI
        return {
            "role": role,
            "goal": goal,
            "backstory": backstory,
            "tools": tools or [],
            "llm": self.client,
            **kwargs
        }

    def supports_mcp_natively(self) -> bool:
        """Gemini doesn't support MCP natively - requires function calling wrapper."""
        return False

    def supports_visual_analysis(self) -> bool:
        """Gemini supports visual analysis with Visual Thinking capability."""
        return True

    def analyze_image(self, image_path: str, prompt: str) -> str:
        """Analyze an image using Gemini's visual capabilities.

        Args:
            image_path: Path to image file
            prompt: Analysis prompt

        Returns:
            Analysis result
        """
        import PIL.Image

        try:
            img = PIL.Image.open(image_path)
            if USE_NEW_API:
                # New API structure
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt, img]
                )
                return response.text
            else:
                # Deprecated API
                response = self.client.generate_content([prompt, img])
                return response.text
        except Exception as e:
            logger.error(f"Gemini image analysis error: {e}")
            raise

