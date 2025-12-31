"""Base MCP client for communicating with MCP servers."""

import json
import subprocess
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)


class BaseMCPClient(ABC):
    """Base class for MCP clients."""

    def __init__(
        self,
        server_path: Optional[Union[str, List[str]]] = None,
        transport: str = "stdio",
        server_url: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        """Initialize MCP client.

        Args:
            server_path: Path to MCP server executable or command list (for stdio transport)
            transport: Transport type ("stdio" or "http")
            server_url: Server URL (for http transport)
            env: Environment variables for the server process
        """
        self.server_path = server_path
        self.transport = transport
        self.server_url = server_url
        self.env = env
        self.process: Optional[subprocess.Popen] = None
        self._tools: Optional[List[Dict[str, Any]]] = None

    @abstractmethod
    def _get_default_server_path(self) -> Union[str, List[str]]:
        """Get default server path if not provided.

        Returns:
            Default server path or command list
        """
        pass

    def _start_stdio_server(self) -> None:
        """Start MCP server as subprocess (stdio transport)."""
        if self.process:
            return

        server_path = self.server_path or self._get_default_server_path()
        
        # Determine command to run
        if isinstance(server_path, str):
            command = [server_path]
        else:
            command = server_path

        # Prepare environment
        import os
        process_env = os.environ.copy()
        if self.env:
            process_env.update(self.env)

        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=process_env,
                shell=True if isinstance(command, list) and "npx" in command[0] else False
            )
            logger.info(f"Started MCP server: {command}")
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise

    def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a request to the MCP server.

        Args:
            method: MCP method name
            params: Request parameters

        Returns:
            Response from server
        """
        if self.transport == "stdio":
            if not self.process:
                self._start_stdio_server()

            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params or {},
            }

            try:
                request_json = json.dumps(request)
                self.process.stdin.write(request_json + "\n")
                self.process.stdin.flush()

                response_line = self.process.stdout.readline()
                response = json.loads(response_line)
                return response
            except Exception as e:
                logger.error(f"MCP request error: {e}")
                raise
        else:
            # HTTP transport implementation would go here
            raise NotImplementedError("HTTP transport not yet implemented")

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server.

        Returns:
            List of tool definitions
        """
        if self._tools is not None:
            return self._tools

        response = self._send_request("tools/list")
        if "result" in response and "tools" in response["result"]:
            self._tools = response["result"]["tools"]
            return self._tools
        return []

    def call_tool(
        self, tool_name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Call a tool on the MCP server.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        response = self._send_request(
            "tools/call",
            params={"name": tool_name, "arguments": arguments or {}},
        )
        if "result" in response:
            return response["result"]
        elif "error" in response:
            raise Exception(f"MCP tool error: {response['error']}")
        return {}

    def close(self) -> None:
        """Close the MCP client connection."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
            logger.info("Closed MCP server connection")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

