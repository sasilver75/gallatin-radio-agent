from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql://quarterback:quarterback@localhost:55432/quarterback",
        alias="DATABASE_URL",
    )
    web_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="WEB_ORIGINS",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_web_origins(self) -> list[str]:
        return [origin.strip() for origin in self.web_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
