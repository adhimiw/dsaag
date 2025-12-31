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

    def get_network_logs(self) -> Dict[str, Any]:
        """Capture network activity logs.

        Returns:
            Network requests and responses
        """
        return self.evaluate_script("""
            return performance.getEntriesByType('resource').map(entry => ({
                url: entry.name,
                duration: entry.duration,
                size: entry.transferSize,
                type: entry.initiatorType,
                startTime: entry.startTime
            }));
        """)

    def get_console_logs(self) -> Dict[str, Any]:
        """Get browser console logs.

        Returns:
            Console messages
        """
        return self.evaluate_script("""
            return console.memory ? {
                jsHeapSizeLimit: console.memory.jsHeapSizeLimit,
                totalJSHeapSize: console.memory.totalJSHeapSize,
                usedJSHeapSize: console.memory.usedJSHeapSize
            } : {message: 'Console memory not available'};
        """)

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics.

        Returns:
            Performance timing data
        """
        return self.evaluate_script("""
            const perfData = performance.getEntriesByType('navigation')[0];
            const paintData = performance.getEntriesByType('paint');
            
            return {
                navigation: perfData ? {
                    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                    loadComplete: perfData.loadEventEnd - perfData.loadEventStart,
                    domInteractive: perfData.domInteractive,
                    domComplete: perfData.domComplete,
                    transferSize: perfData.transferSize,
                    encodedBodySize: perfData.encodedBodySize,
                    decodedBodySize: perfData.decodedBodySize
                } : null,
                paint: paintData.map(p => ({name: p.name, time: p.startTime})),
                memory: performance.memory ? {
                    jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
                    totalJSHeapSize: performance.memory.totalJSHeapSize,
                    usedJSHeapSize: performance.memory.usedJSHeapSize
                } : null
            };
        """)

    def extract_table_data(self, table_selector: str) -> Dict[str, Any]:
        """Extract data from an HTML table.

        Args:
            table_selector: CSS selector for the table

        Returns:
            Table data as array of arrays
        """
        return self.evaluate_script(f"""
            const table = document.querySelector('{table_selector}');
            if (!table) return {{error: 'Table not found'}};
            
            const rows = Array.from(table.querySelectorAll('tr'));
            return {{
                headers: Array.from(rows[0]?.querySelectorAll('th') || []).map(th => th.textContent.trim()),
                rows: rows.slice(1).map(row => 
                    Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim())
                )
            }};
        """)

    def extract_json_from_script(self, pattern: str = "window.__DATA__") -> Dict[str, Any]:
        """Extract JSON data from inline scripts.

        Args:
            pattern: Variable name or pattern to search for

        Returns:
            Extracted JSON data
        """
        return self.evaluate_script(f"""
            try {{
                return {pattern};
            }} catch(e) {{
                return {{error: 'Data not found or not valid JSON', message: e.message}};
            }}
        """)

    def monitor_api_calls(self, url_pattern: str) -> Dict[str, Any]:
        """Monitor and capture API calls matching a pattern.

        Args:
            url_pattern: URL pattern to match (regex)

        Returns:
            Captured API calls
        """
        return self.evaluate_script(f"""
            const pattern = new RegExp('{url_pattern}');
            return performance.getEntriesByType('resource')
                .filter(entry => pattern.test(entry.name))
                .map(entry => ({{  
                    url: entry.name,
                    duration: entry.duration,
                    size: entry.transferSize,
                    type: entry.initiatorType
                }}));
        """)

    def scroll_to_bottom(self) -> Dict[str, Any]:
        """Scroll page to bottom to trigger lazy loading.

        Returns:
            Scroll result
        """
        return self.evaluate_script("""
            window.scrollTo(0, document.body.scrollHeight);
            return {scrolled: true, height: document.body.scrollHeight};
        """)

    def get_page_metadata(self) -> Dict[str, Any]:
        """Extract page metadata (title, description, etc.).

        Returns:
            Page metadata
        """
        return self.evaluate_script("""
            return {
                title: document.title,
                description: document.querySelector('meta[name="description"]')?.content,
                keywords: document.querySelector('meta[name="keywords"]')?.content,
                url: window.location.href,
                domain: window.location.hostname,
                protocol: window.location.protocol,
                viewport: {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            };
        """)

