from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

class Settings(BaseSettings):
    MONGO_URL: str
    POSTGRES_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    
    model_config = SettingsConfigDict(env_file=".env")

try:
    settings = Settings()
except Exception as e:
    logging.critical("Failed to load environment variables")
    raise SystemExit("Config error, sytem shutting down")