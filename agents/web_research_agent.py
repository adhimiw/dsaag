"""Web Research Agent for external searches and scraping."""

from typing import Any, List, Optional

from crewai import Agent
from crewai.tools import BaseTool

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llm.base_llm import BaseLLM
from llm.factory import get_llm
from mcp_clients.browser_client import BrowserMCPClient
from utils.logger import get_logger
from agents.base_agent import BaseAgent

logger = get_logger(__name__)


class WebResearchAgent(BaseAgent):
    """Web Research Agent that performs external searches and scrapes information."""

    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        browser_client: Optional[BrowserMCPClient] = None,
        **kwargs: Any
    ):
        """Initialize Web Research Agent.

        Args:
            llm: Optional LLM instance
            browser_client: Optional Browser MCP client
            **kwargs: Additional arguments
        """
        role = "Web Research Specialist"
        goal = "Perform external searches and scrape relevant information from the web"
        backstory = """You are an expert at web research and information gathering.
        You can navigate search engines, extract information from web pages, and scrape content from sites like Reddit.
        You excel at finding relevant, up-to-date information to answer questions."""

        # Use Mistral by default (has built-in Websearch connector)
        # Can also use Browser MCP for complex scraping
        if llm is None:
            llm = get_llm(provider="mistral")

        # Create MCP tools for CrewAI
        tools = self._create_mcp_tools(browser_client)

        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            tools=tools,
            **kwargs
        )

        self.browser_client = browser_client

        logger.info("Web Research Agent initialized")

    def _create_mcp_tools(
        self,
        browser_client: Optional[BrowserMCPClient],
    ) -> List[BaseTool]:
        """Create CrewAI tools from MCP clients.

        Args:
            browser_client: Browser MCP client

        Returns:
            List of CrewAI tools
        """
        tools = []

        # For now, return empty list
        # In full implementation:
        # - Use Mistral's built-in Websearch connector for simple searches
        # - Use Browser MCP client for complex scraping (Reddit, dynamic content)
        # - Expose MCP tools natively to Mistral if using Mistral Agents API

        return tools

    def search_web(self, query: str, use_mistral_websearch: bool = True) -> dict:
        """Perform a web search.

        Args:
            query: Search query
            use_mistral_websearch: Whether to use Mistral's built-in Websearch

        Returns:
            Search results
        """
        logger.info(f"Searching web for: {query}")

        if use_mistral_websearch and self.llm.supports_mcp_natively():
            # Use Mistral's built-in Websearch connector
            # This would be handled via Mistral's native tool support
            pass

        # Fallback to Browser MCP for complex searches
        if self.browser_client:
            # Navigate to Google, perform search, extract results
            pass

        return {
            "query": query,
            "results": [],
            "status": "pending"
        }

    def scrape_page(self, url: str) -> dict:
        """Scrape content from a web page.

        Args:
            url: URL to scrape

        Returns:
            Scraped content
        """
        logger.info(f"Scraping page: {url}")

        if self.browser_client:
            # Use Browser MCP to navigate and scrape
            result = self.browser_client.navigate_page(url)
            # Extract content using evaluate_script
            return {
                "url": url,
                "content": "",
                "status": "pending"
            }

        return {"url": url, "content": "", "status": "error"}

