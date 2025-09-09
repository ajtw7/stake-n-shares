from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    USE_EXTERNAL_APIS: bool = False
    ALPACA_API_KEY: str | None = None
    ALPACA_API_SECRET: str | None = None
    ALPACA_BASE_URL: str | None = None
    ODDS_API_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()