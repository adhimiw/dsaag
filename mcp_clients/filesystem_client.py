"""Filesystem MCP client for file operations."""

from typing import Any, Dict, List, Optional

from utils.logger import get_logger
from .base_mcp_client import BaseMCPClient

logger = get_logger(__name__)


class FilesystemMCPClient(BaseMCPClient):
    """Client for Filesystem MCP Server."""

    def _get_default_server_path(self) -> List[str]:
        """Get default Filesystem MCP server path."""
        import os
        # Allow access to the current project directory and data directory
        cwd = os.getcwd()
        return ["npx", "-y", "@modelcontextprotocol/server-filesystem", cwd]

    def read_text_file(
        self,
        path: str,
        head: Optional[int] = None,
        tail: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Read a text file.

        Args:
            path: File path
            head: Number of lines to read from start
            tail: Number of lines to read from end

        Returns:
            File content
        """
        params = {"path": path}
        if head:
            params["head"] = head
        if tail:
            params["tail"] = tail

        return self.call_tool("read_text_file", params)

    def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file.

        Args:
            path: File path
            content: Content to write

        Returns:
            Write operation result
        """
        return self.call_tool("write_file", {"path": path, "content": content})

    def edit_file(
        self,
        path: str,
        edits: List[Dict[str, str]],
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Edit a file with selective changes.

        Args:
            path: File path
            edits: List of edits with oldText and newText
            dry_run: Whether to perform a dry run

        Returns:
            Edit operation result
        """
        return self.call_tool(
            "edit_file",
            {
                "path": path,
                "edits": edits,
                "dryRun": dry_run,
            },
        )

    def list_directory(self, path: str) -> Dict[str, Any]:
        """List directory contents.

        Args:
            path: Directory path

        Returns:
            Directory listing
        """
        return self.call_tool("list_directory", {"path": path})

    def search_files(
        self,
        path: str,
        pattern: str,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Search for files matching a pattern.

        Args:
            path: Search root path
            pattern: File pattern to match
            exclude_patterns: Patterns to exclude

        Returns:
            Search results
        """
        params = {"path": path, "pattern": pattern}
        if exclude_patterns:
            params["excludePatterns"] = exclude_patterns

        return self.call_tool("search_files", params)

    def create_directory(self, path: str) -> Dict[str, Any]:
        """Create a directory.

        Args:
            path: Directory path

        Returns:
            Creation result
        """
        return self.call_tool("create_directory", {"path": path})

