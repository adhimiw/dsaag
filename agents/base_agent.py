"""Base agent class for all agents."""

from typing import Any, List, Optional

from crewai import Agent
from crewai.tools import BaseTool

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_settings
from llm.base_llm import BaseLLM
from llm.factory import get_llm
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseAgent:
    """Base class for all agents with LLM and MCP client access."""

    def __init__(
        self,
        role: str,
        goal: str,
        backstory: str,
        llm: Optional[BaseLLM] = None,
        tools: Optional[List[BaseTool]] = None,
        llm_provider: Optional[str] = None,
        **kwargs: Any
    ):
        """Initialize base agent.

        Args:
            role: Agent role
            goal: Agent goal
            backstory: Agent backstory
            llm: Optional LLM instance (defaults to primary provider)
            tools: Optional list of tools
            llm_provider: Optional LLM provider override
            **kwargs: Additional CrewAI Agent arguments
        """
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.settings = get_settings()

        # Initialize LLM
        if llm is None:
            # Use Mistral by default (native MCP support)
            # Use Gemini for visual analysis tasks
            provider = llm_provider or self._select_llm_provider()
            self.llm = get_llm(provider=provider)
        else:
            self.llm = llm

        # Create CrewAI agent
        self.agent = self._create_crewai_agent(tools=tools, **kwargs)

        logger.info(f"Created agent: {role} using {self.llm.__class__.__name__}")

    def _select_llm_provider(self) -> str:
        """Select appropriate LLM provider based on agent type.

        Returns:
            LLM provider name
        """
        # Default to Mistral for most agents (native MCP advantage)
        # Override in subclasses for visual analysis tasks
        return self.settings.primary_llm_provider

    def _create_crewai_agent(
        self, tools: Optional[List[BaseTool]] = None, **kwargs: Any
    ) -> Agent:
        """Create CrewAI agent instance.

        Args:
            tools: Optional list of tools
            **kwargs: Additional arguments (may include allow_delegation)

        Returns:
            CrewAI Agent instance
        """
        # Convert LLM to CrewAI format
        # CrewAI expects an LLM instance that matches its interface
        # We'll need to adapt our LLM wrapper
        llm_for_crewai = self._adapt_llm_for_crewai()

        # Extract allow_delegation from kwargs if present, otherwise default to False
        allow_delegation = kwargs.pop("allow_delegation", False)
        
        # Create agent with our custom LLM directly
        # Pass the LLM wrapper directly to avoid CrewAI trying to create default LLM
        agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=tools or [],
            llm=llm_for_crewai,  # Pass our custom LLM directly
            verbose=True,
            allow_delegation=allow_delegation,
            **kwargs
        )
        
        return agent

    def _adapt_llm_for_crewai(self) -> Any:
        """Adapt our LLM wrapper for CrewAI compatibility.

        Returns:
            CrewAI-compatible LLM instance
        """
        from crewai import LLM
        
        # Determine model string and API key from self.llm
        model_name = getattr(self.llm, "model", "")
        api_key = getattr(self.llm, "api_key", None)
        
        # Ensure correct prefix for LiteLLM
        if "Mistral" in self.llm.__class__.__name__:
             if not model_name.startswith("mistral/"):
                model_name = f"mistral/{model_name}"
        elif "Google" in self.llm.__class__.__name__:
             # Google/Gemini usually uses 'gemini/' prefix in LiteLLM
             if not model_name.startswith("gemini/") and not model_name.startswith("google/"):
                model_name = f"gemini/{model_name}"
        
        # Return standard CrewAI LLM object
        return LLM(model=model_name, api_key=api_key)

    def execute(self, task: str) -> str:
        """Execute a task using this agent.

        Args:
            task: Task description

        Returns:
            Task execution result
        """
        # This would be used with CrewAI's Crew
        # For now, return a placeholder
        return f"Agent {self.role} executing: {task}"

    def get_agent(self) -> Agent:
        """Get the underlying CrewAI agent.

        Returns:
            CrewAI Agent instance
        """
        return self.agent

