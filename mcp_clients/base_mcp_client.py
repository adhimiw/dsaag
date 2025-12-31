"""Fixed Base MCP client with proper protocol implementation."""

import json
import subprocess
import time
import threading
import queue
import select
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from utils.logger import get_logger

logger = get_logger(__name__)


class BaseMCPClient(ABC):
    """Base class for MCP clients with proper protocol support."""

    def __init__(
        self,
        server_path: Optional[Union[str, List[str]]] = None,
        transport: str = "stdio",
        server_url: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        self.server_path = server_path
        self.transport = transport
        self.server_url = server_url
        self.env = env
        self.process: Optional[subprocess.Popen] = None
        self._tools: Optional[List[Dict[str, Any]]] = None
        self._initialized = False
        self._request_id = 0
        self._stderr_thread: Optional[threading.Thread] = None
        self._stdout_thread: Optional[threading.Thread] = None
        self._response_queue = queue.Queue()
        self._pending_requests = {}
        self._running = False

    @abstractmethod
    def _get_default_server_path(self) -> Union[str, List[str]]:
        """Get default server path if not provided."""
        pass

    def _get_next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    def _monitor_stderr(self):
        """Monitor stderr for server errors."""
        if not self.process or not self.process.stderr:
            return

        try:
            for line in self.process.stderr:
                if line:
                    logger.debug(f"MCP Server stderr: {line.strip()}")
        except Exception as e:
            logger.debug(f"Stderr monitoring ended: {e}")

    def _monitor_stdout(self):
        """Monitor stdout and queue responses."""
        if not self.process or not self.process.stdout:
            return

        try:
            while self._running:
                line = self.process.stdout.readline()
                if not line:
                    break

                try:
                    data = json.loads(line.strip())
                    self._response_queue.put(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON response: {line[:100]}... Error: {e}")
        except Exception as e:
            logger.debug(f"Stdout monitoring ended: {e}")

    def _start_stdio_server(self) -> None:
        """Start MCP server as subprocess (stdio transport)."""
        if self.process:
            return

        server_path = self.server_path or self._get_default_server_path()

        if isinstance(server_path, str):
            command = [server_path]
        else:
            command = server_path

        import os
        process_env = os.environ.copy()
        if self.env:
            process_env.update({k: v for k, v in self.env.items() if v is not None})

        try:
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=process_env,
            )
            self._running = True
            logger.info(f"Started MCP server: {command}")

            self._stderr_thread = threading.Thread(
                target=self._monitor_stderr, daemon=True
            )
            self._stderr_thread.start()

            self._stdout_thread = threading.Thread(
                target=self._monitor_stdout, daemon=True
            )
            self._stdout_thread.start()

            time.sleep(2)

            self._initialize_mcp()

        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            raise

    def _initialize_mcp(self):
        """Perform MCP initialization handshake."""
        if self._initialized:
            return

        logger.info("Initializing MCP connection...")

        init_request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "data-analytics-agent",
                    "version": "0.1.0"
                }
            }
        }

        try:
            request_json = json.dumps(init_request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()

            response = self._wait_for_response(timeout=10)

            if not response:
                raise Exception("No response from server during initialization")

            if "error" in response:
                raise Exception(f"MCP init error: {response['error']}")

            logger.info(f"Server initialized with capabilities: {response.get('result', {}).get('capabilities', {})}")

            initialized_notif = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }

            notif_json = json.dumps(initialized_notif) + "\n"
            self.process.stdin.write(notif_json)
            self.process.stdin.flush()

            self._initialized = True
            logger.info("MCP client initialized successfully")

        except Exception as e:
            logger.error(f"MCP initialization failed: {e}")
            raise

    def _wait_for_response(self, timeout: float = 30) -> Optional[Dict[str, Any]]:
        """Wait for a response from the response queue."""
        try:
            response = self._response_queue.get(timeout=timeout)
            return response
        except queue.Empty:
            logger.error(f"Timeout waiting for response after {timeout}s")
            return None

    def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a request to the MCP server."""
        if self.transport == "stdio":
            if not self.process or not self._running:
                self._start_stdio_server()

            if not self._initialized:
                self._initialize_mcp()

            request_id = self._get_next_id()
            request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": method,
                "params": params or {},
            }

            try:
                request_json = json.dumps(request) + "\n"
                self.process.stdin.write(request_json)
                self.process.stdin.flush()

                response = self._wait_for_response(timeout=30)

                if not response:
                    raise TimeoutError(f"MCP server response timeout for method: {method}")

                if "error" in response:
                    raise Exception(f"MCP error for {method}: {response['error']}")

                return response

            except Exception as e:
                logger.error(f"MCP request error for {method}: {e}")
                raise
        else:
            raise NotImplementedError("HTTP transport not yet implemented")

    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
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
        """Call a tool on the MCP server."""
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
        self._running = False

        if self.process:
            try:
                self.process.stdin.close()
            except:
                pass

            self.process.terminate()

            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

            self.process = None
            logger.info("Closed MCP server connection")

        if self._stderr_thread and self._stderr_thread.is_alive():
            self._stderr_thread.join(timeout=1)

        if self._stdout_thread and self._stdout_thread.is_alive():
            self._stdout_thread.join(timeout=1)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
