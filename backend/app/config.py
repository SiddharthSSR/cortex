"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    environment: str = "development"

    # CORS Settings
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    # MLX Model Configuration
    default_model: str = "mlx-community/Llama-3.2-3B-Instruct-4bit"
    model_cache_dir: str = "~/.cache/mlx-models"

    # Generation Settings
    default_max_tokens: int = 2048
    default_temperature: float = 0.7
    default_top_p: float = 0.9

    # Tool Settings
    enable_web_search: bool = True
    enable_code_execution: bool = True
    enable_file_operations: bool = False
    code_execution_timeout: int = 30

    # Agent Settings
    enable_agents: bool = True
    max_agent_iterations: int = 10
    agent_timeout: int = 300

    # Optional API Keys for external tools
    openweather_api_key: Optional[str] = None
    serper_api_key: Optional[str] = None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
