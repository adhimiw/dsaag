"""Terminal/Shell MCP client for command execution."""

from typing import Any, Dict, List, Optional

from utils.logger import get_logger
from .base_mcp_client import BaseMCPClient

logger = get_logger(__name__)


class TerminalMCPClient(BaseMCPClient):
    """Client for Terminal/Shell MCP Server."""

    def _get_default_server_path(self) -> str:
        """Get default Terminal MCP server path."""
        return "shell-command-mcp"

    def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute a shell command.

        Args:
            command: Command to execute
            timeout: Execution timeout in seconds

        Returns:
            Command execution result
        """
        params = {"command": command}
        if timeout:
            params["timeout"] = timeout

        return self.call_tool("execute_command", params)

    def run_script(
        self,
        path: str,
        args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute a script file.

        Args:
            path: Path to script file
            args: Optional script arguments

        Returns:
            Script execution result
        """
        params = {"path": path}
        if args:
            params["args"] = args

        return self.call_tool("run_script", params)

    def get_process_status(self, pid: int) -> Dict[str, Any]:
        """Get status of a running process.

        Args:
            pid: Process ID

        Returns:
            Process status
        """
        return self.call_tool("get_process_status", {"pid": pid})

