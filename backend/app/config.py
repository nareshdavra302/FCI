from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "FCI Platform"
    debug: bool = False
    log_level: str = "INFO"

    database_url: str = "postgresql://fci:fci@localhost:5432/fci"

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    llm_provider: Literal["openai", "anthropic", "mock"] = "mock"
    llm_api_key: str = ""
    llm_model: str = ""

    planner_window_minutes: int = 5

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def llm_enabled(self) -> bool:
        return self.llm_provider != "mock" and bool(self.llm_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
