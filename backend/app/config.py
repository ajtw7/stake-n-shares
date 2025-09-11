from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    USE_EXTERNAL_APIS: bool = False
    ALPACA_API_KEY: str | None = None
    ALPACA_API_SECRET: str | None = None
    ALPACA_BASE_URL: str | None = None
    ODDS_API_KEY: str | None = None

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # ignore unexpected env vars instead of error
    )

settings = Settings()