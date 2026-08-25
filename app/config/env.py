from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # db
    DB_HOST: str
    DB_PORT: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE_NAME: str

    # redis
    REDIS_HOST: str
    REDIS_PORT: str

    # llm
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()