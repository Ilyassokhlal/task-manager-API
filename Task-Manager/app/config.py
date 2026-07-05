from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name : str = "Task Manager API"
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

