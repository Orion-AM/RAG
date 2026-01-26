
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    CHROMA_DB_DIR: str = "./chroma_db"
    SQL_DB_URL: str = "sqlite:///./sql.db"
    MONGO_DB_URL: str = "mongodb://localhost:27017"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
