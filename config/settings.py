"""Configuration settings management using Pydantic Settings."""

from pathlib import Path
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # LLM Provider Configuration
    mistral_api_key: str = Field(..., description="Mistral AI API key")
    google_api_key: Optional[str] = Field(None, description="Google Gemini API key (optional)")
    primary_llm_provider: Literal["mistral", "google"] = Field(
        default="mistral", description="Primary LLM provider"
    )

    # MCP Server Configuration
    mcp_server_transport: Literal["stdio", "http"] = Field(
        default="stdio", description="MCP server transport type"
    )
    jupyter_mcp_server_path: Optional[str] = Field(
        None, description="Path to Jupyter MCP server executable"
    )
    jupyter_token: Optional[str] = Field(None, description="Jupyter Server Token")
    jupyter_url: str = Field(default="http://localhost:8888", description="Jupyter Server URL")
    browser_mcp_server_path: Optional[str] = Field(
        None, description="Path to Browser/Chrome DevTools MCP server executable"
    )
    filesystem_mcp_server_path: Optional[str] = Field(
        None, description="Path to Filesystem MCP server executable"
    )
    terminal_mcp_server_path: Optional[str] = Field(
        None, description="Path to Terminal/Shell MCP server executable"
    )

    # Project Paths
    project_root: str = Field(default=".", description="Project root directory")
    data_dir: Path = Field(default=Path("./data"), description="Data storage directory")
    notebooks_dir: Path = Field(
        default=Path("./notebooks"), description="Generated notebooks directory"
    )
    outputs_dir: Path = Field(
        default=Path("./outputs"), description="Analysis outputs directory"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[Path] = Field(None, description="Log file path")

    def __init__(self, **kwargs):
        """Initialize settings and create necessary directories."""
        super().__init__(**kwargs)
        # Create directories if they don't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "uploads").mkdir(parents=True, exist_ok=True)
        self.notebooks_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

