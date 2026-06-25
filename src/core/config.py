from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="Semantic Resume Matcher", alias="APP_NAME")
    database_url: str = Field(
        default="postgresql+psycopg://resume_matcher:resume_matcher@localhost:5432/resume_matcher",
        alias="DATABASE_URL",
    )
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    prompt_dir: str = Field(default="prompts", alias="PROMPT_DIR")

    use_ollama: bool = Field(default=True, alias="USE_OLLAMA")
    ollama_base_url: str = Field(
        default="http://host.docker.internal:11434", alias="OLLAMA_BASE_URL"
    )
    ollama_llm_model: str = Field(default="llama3.2", alias="OLLAMA_LLM_MODEL")
    ollama_embed_model: str = Field(default="nomic-embed-text", alias="OLLAMA_EMBED_MODEL")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

