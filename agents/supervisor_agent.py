"""Supervisor Agent for orchestrating the workflow."""

from typing import Any, List, Optional

from crewai import Agent
from crewai.tools import BaseTool

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import get_settings
from llm.base_llm import BaseLLM
from llm.factory import get_llm
from utils.logger import get_logger
from agents.base_agent import BaseAgent

logger = get_logger(__name__)


class SupervisorAgent(BaseAgent):
    """Supervisor Agent that orchestrates the entire workflow."""

    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        tools: Optional[List[BaseTool]] = None,
        **kwargs: Any
    ):
        """Initialize Supervisor Agent.

        Args:
            llm: Optional LLM instance (defaults to Mistral for planning)
            tools: Optional list of tools
            **kwargs: Additional arguments
        """
        role = "Supervisor and Orchestrator"
        goal = "Coordinate the data analytics workflow, delegate tasks to specialized agents, and synthesize final results"
        backstory = """You are an expert at breaking down complex data analytics tasks into manageable steps.
        You understand the full data science workflow from data ingestion to predictive modeling.
        You excel at routing tasks to the right specialist agent and ensuring quality results."""

        # Supervisor uses Mistral for its planning capabilities
        if llm is None:
            llm = get_llm(provider="mistral", model="mistral-large-latest")

        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            tools=tools,
            allow_delegation=True,  # Supervisor can delegate - passed via kwargs
            **kwargs
        )

        logger.info("Supervisor Agent initialized with Mistral Agents API")

    def route_task(self, task_description: str) -> str:
        """Route a task to the appropriate agent.

        Args:
            task_description: Description of the task

        Returns:
            Agent name to handle the task
        """
        # Use Mistral's planning to determine task routing
        routing_prompt = f"""Given this task: {task_description}

Determine which agent should handle it:
- Data Ingestion Agent: For loading, validating, and cleaning data
- EDA & RAG Agent: For exploratory data analysis and visualization
- Analysis Decision Agent: For determining if predictive modeling is suitable
- Predictive Modeling Agent: For training and evaluating models
- Web Research Agent: For external web searches and scraping
- Conversational Agent: For answering user questions

Respond with just the agent name."""

        try:
            response = self.llm.generate(routing_prompt)
            return response.strip()
        except Exception as e:
            logger.error(f"Task routing error: {e}")
            return "Supervisor Agent"  # Default fallback

