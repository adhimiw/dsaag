"""Data Ingestion Agent for loading and validating data."""

from typing import Any, List, Optional

from crewai import Agent
from crewai.tools import BaseTool

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llm.base_llm import BaseLLM
from llm.factory import get_llm
from mcp_clients.filesystem_client import FilesystemMCPClient
from mcp_clients.terminal_client import TerminalMCPClient
from utils.logger import get_logger
from agents.base_agent import BaseAgent

logger = get_logger(__name__)


class DataIngestionAgent(BaseAgent):
    """Data Ingestion Agent that loads, validates, and cleans user-provided data."""

    def __init__(
        self,
        llm: Optional[BaseLLM] = None,
        filesystem_client: Optional[FilesystemMCPClient] = None,
        terminal_client: Optional[TerminalMCPClient] = None,
        **kwargs: Any
    ):
        """Initialize Data Ingestion Agent.

        Args:
            llm: Optional LLM instance
            filesystem_client: Optional Filesystem MCP client
            terminal_client: Optional Terminal MCP client
            **kwargs: Additional arguments
        """
        role = "Data Ingestion Specialist"
        goal = "Load, validate, and clean user-provided data, generating data schema and quality reports"
        backstory = """You are an expert at data validation and quality assessment.
        You understand various data formats (CSV, JSON, Excel, Parquet) and can identify data quality issues.
        You excel at generating comprehensive data schemas and cleaning logs."""

        # Use Mistral by default (native MCP support)
        if llm is None:
            llm = get_llm(provider="mistral")

        # Create MCP tools for CrewAI
        tools = self._create_mcp_tools(filesystem_client, terminal_client)

        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            tools=tools,
            **kwargs
        )

        self.filesystem_client = filesystem_client
        self.terminal_client = terminal_client

        logger.info("Data Ingestion Agent initialized")

    def _create_mcp_tools(
        self,
        filesystem_client: Optional[FilesystemMCPClient],
        terminal_client: Optional[TerminalMCPClient],
    ) -> List[BaseTool]:
        """Create CrewAI tools from MCP clients.

        Args:
            filesystem_client: Filesystem MCP client
            terminal_client: Terminal MCP client

        Returns:
            List of CrewAI tools
        """
        tools = []
        
        # Import tool decorator needed for the wrapper methods
        from crewai.tools import tool

        if filesystem_client:
            @tool("Write File")
            def write_file(path: str, content: str) -> str:
                """Write content to a file at the specified path.
                Args:
                    path: The absolute path to write the file to.
                    content: The text content to write.
                Returns:
                        A success message or error description.
                """
                try:
                    filesystem_client.write_file(path, content)
                    return f"Successfully wrote to {path}"
                except Exception as e:
                    return f"Error writing file: {e}"

            @tool("Read File")
            def read_file(path: str) -> str:
                """Read text content from a file.
                Args:
                        path: The absolute path of the file to read.
                Returns:
                        The content of the file or error message.
                """
                try:
                    result = filesystem_client.read_text_file(path)
                    if isinstance(result, dict) and 'content' in result:
                            return result['content']
                    return str(result)
                except Exception as e:
                        return f"Error reading file: {e}"
                
            tools.append(write_file)
            tools.append(read_file)

        return tools

    def ingest_data(self, file_path: str) -> dict:
        """Ingest data from a file.

        Args:
            file_path: Path to data file

        Returns:
            Data schema and cleaning log
        """
        logger.info(f"Ingesting data from: {file_path}")

        # This would use the MCP clients to read and process the file
        # For now, return a placeholder structure
        return {
            "file_path": file_path,
            "schema": {},
            "cleaning_log": [],
            "status": "pending"
        }

