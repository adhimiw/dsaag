"""Browser/Chrome DevTools MCP client for web automation."""

from typing import Any, Dict, List, Optional, Union

from utils.logger import get_logger
from .base_mcp_client import BaseMCPClient

logger = get_logger(__name__)


class BrowserMCPClient(BaseMCPClient):
    """Client for Chrome DevTools MCP Server."""

    def _get_default_server_path(self) -> Union[str, List[str]]:
        """Get default Browser MCP server path."""
        # Use npx to run the latest version of chrome-devtools-mcp
        return ["npx", "-y", "chrome-devtools-mcp@latest"]

    def navigate_page(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL.

        Args:
            url: URL to navigate to

        Returns:
            Navigation result
        """
        return self.call_tool("navigate_page", {"url": url})

    def fill(self, selector: str, text: str) -> Dict[str, Any]:
        """Fill a form field.

        Args:
            selector: CSS selector for the field
            text: Text to fill

        Returns:
            Fill operation result
        """
        return self.call_tool("fill", {"selector": selector, "text": text})

    def fill_form(self, fields: Dict[str, str]) -> Dict[str, Any]:
        """Fill multiple form fields.

        Args:
            fields: Dictionary mapping selectors to values

        Returns:
            Form fill result
        """
        return self.call_tool("fill_form", {"fields": fields})

    def click(self, selector: str) -> Dict[str, Any]:
        """Click on an element.

        Args:
            selector: CSS selector for the element

        Returns:
            Click operation result
        """
        return self.call_tool("click", {"selector": selector})

    def evaluate_script(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript in the browser context.

        Args:
            script: JavaScript code to execute

        Returns:
            Script execution result
        """
        return self.call_tool("evaluate_script", {"script": script})

    def take_screenshot(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot of the current page.

        Args:
            path: Optional path to save screenshot

        Returns:
            Screenshot result
        """
        params = {}
        if path:
            params["path"] = path
        return self.call_tool("take_screenshot", params)

    def wait_for(self, condition: str) -> Dict[str, Any]:
        """Wait for a condition to be met.

        Args:
            condition: Condition to wait for (e.g., "element visible: #id")

        Returns:
            Wait operation result
        """
        return self.call_tool("wait_for", {"condition": condition})

