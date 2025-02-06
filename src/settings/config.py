from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_KEY: str
    BASE_URL_1: str
    BASE_URL_2: str
    DB_NAME: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
