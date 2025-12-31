"""Code Executor MCP client for local Python execution."""

from typing import Any, Dict, List, Optional, Union

from utils.logger import get_logger
from .base_mcp_client import BaseMCPClient

logger = get_logger(__name__)


class CodeExecutorMCPClient(BaseMCPClient):
    """Client for Code Executor MCP Server (fallback for Jupyter)."""

    def _get_default_server_path(self) -> Union[str, List[str]]:
        """Get default Code Executor MCP server path."""
        return ["node", "./mcp_code_executor/build/index.js"]

    def execute_code(
        self,
        code: str,
        timeout: Optional[int] = None,
        environment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Execute Python code in the specified environment.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            environment: Optional environment override

        Returns:
            Execution result with output and any errors
        """
        params = {"code": code}
        
        if timeout:
            params["timeout"] = timeout
        
        if environment:
            params["environment"] = environment

        return self.call_tool("execute_python", params)

    def install_package(
        self,
        package_name: str,
        version: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Install a Python package in the environment.

        Args:
            package_name: Name of the package to install
            version: Optional specific version

        Returns:
            Installation result
        """
        params = {"package": package_name}
        
        if version:
            params["version"] = version

        return self.call_tool("install_package", params)

    def check_package(
        self,
        package_name: str,
    ) -> Dict[str, Any]:
        """Check if a package is installed.

        Args:
            package_name: Name of the package to check

        Returns:
            Package status
        """
        return self.call_tool("check_package", {"package": package_name})

    def list_packages(self) -> Dict[str, Any]:
        """List all installed packages in the environment.

        Returns:
            List of installed packages
        """
        return self.call_tool("list_packages", {})

    def get_environment_info(self) -> Dict[str, Any]:
        """Get information about the execution environment.

        Returns:
            Environment information
        """
        return self.call_tool("environment_info", {})
