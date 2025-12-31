import sys
from pathlib import Path
import json

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp_clients.jupyter_client import JupyterMCPClient
from mcp_clients.filesystem_client import FilesystemMCPClient

from config.settings import get_settings

def debug_tools():
    print("Debugging Jupyter MCP Client...")
    try:
        settings = get_settings()
        env = {
            "JUPYTER_URL": settings.jupyter_url,
            "JUPYTER_TOKEN": settings.jupyter_token,
            "ALLOW_IMG_OUTPUT": "true"
        }
        # Filter out None values
        env = {k: v for k, v in env.items() if v is not None}
        import time
        time.sleep(2) # Wait for potential server startup
        jupyter_client = JupyterMCPClient(env=env)
        # Give it a moment to initialize connection
        time.sleep(5)
        tools = jupyter_client.list_tools()
        print(f"Found {len(tools)} Jupyter tools:")
        print(json.dumps(tools, indent=2))
        jupyter_client.close()
    except Exception as e:
        print(f"Jupyter Client Error: {e}")

    print("\nDebugging Filesystem MCP Client...")
    try:
        # For filesystem, we need to specific path if we use the default
        # But here we want to see what happens with current default
        fs_client = FilesystemMCPClient()
        tools = fs_client.list_tools()
        print(f"Found {len(tools)} Filesystem tools:")
        print(json.dumps(tools, indent=2))
        fs_client.close()
    except Exception as e:
        print(f"Filesystem Client Error: {e}")

if __name__ == "__main__":
    debug_tools()
