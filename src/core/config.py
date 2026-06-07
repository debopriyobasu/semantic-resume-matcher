from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Semantic Resume Matcher", alias="APP_NAME")
    database_url: str = Field(
        default="postgresql://resume_matcher:resume_matcher@localhost:5432/resume_matcher",
        alias="DATABASE_URL",
    )
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
