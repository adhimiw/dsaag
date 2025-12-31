"""Jupyter MCP client for notebook operations."""

from typing import Any, Dict, List, Optional, Union

from utils.logger import get_logger
from .base_mcp_client import BaseMCPClient

logger = get_logger(__name__)


class JupyterMCPClient(BaseMCPClient):
    """Client for Jupyter MCP Server."""

    def _get_default_server_path(self) -> Union[str, List[str]]:
        """Get default Jupyter MCP server path."""
        # Use uvx to run the latest version of jupyter-mcp-server
        return ["uvx", "jupyter-mcp-server@latest"]

    def use_notebook(
        self,
        notebook_name: str,
        notebook_path: Optional[str] = None,
        mode: str = "create",
    ) -> Dict[str, Any]:
        """Connect to or create a notebook.

        Args:
            notebook_name: Name of the notebook
            notebook_path: Path to notebook file
            mode: "connect" or "create"

        Returns:
            Notebook connection result
        """
        return self.call_tool(
            "use_notebook",
            {
                "notebook_name": notebook_name,
                "notebook_path": notebook_path,
                "mode": mode,
            },
        )

    def insert_execute_code_cell(
        self,
        cell_index: int,
        cell_source: str,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Insert and execute a code cell.

        Args:
            cell_index: Index where to insert the cell
            cell_source: Python code to execute
            timeout: Execution timeout in seconds

        Returns:
            Cell execution result
        """
        params = {
            "index": cell_index,
            "code": cell_source,
        }
        if timeout:
            params["timeout"] = timeout

        return self.call_tool("insert_execute_code_cell", params)

    def execute_cell(
        self,
        cell_index: int,
        timeout: Optional[int] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Execute an existing cell.

        Args:
            cell_index: Index of cell to execute
            timeout: Execution timeout in seconds
            stream: Whether to stream output

        Returns:
            Cell execution result
        """
        params = {
            "index": cell_index,
            "stream": stream,
        }
        if timeout:
            params["timeout"] = timeout

        return self.call_tool("execute_cell", params)

    def read_notebook(
        self,
        notebook_name: str,
        response_format: str = "brief",
    ) -> Dict[str, Any]:
        """Read notebook structure and content.

        Args:
            notebook_name: Name of the notebook
            response_format: "brief" or "detailed"

        Returns:
            Notebook content
        """
        return self.call_tool(
            "read_notebook",
            {
                "notebook_name": notebook_name,
                "response_format": response_format,
            },
        )

    def list_files(
        self,
        path: str = ".",
        max_depth: Optional[int] = None,
        pattern: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List files in Jupyter server filesystem.

        Args:
            path: Directory path
            max_depth: Maximum depth to traverse
            pattern: File pattern to match

        Returns:
            List of files
        """
        params = {"path": path}
        if max_depth:
            params["max_depth"] = max_depth
        if pattern:
            params["pattern"] = pattern

        return self.call_tool("list_files", params)

