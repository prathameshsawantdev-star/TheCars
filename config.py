from pydantic_settings import BaseSettings, SettingsConfigDict 
from typing import Optional

class BaseConfig(BaseSettings):
    DB_URL: Optional[str]
    DB_NAME: Optional[str]
    CLOUDINARY_SECRET_KEY: Optional[str]
    CLOUDINARY_API_KEY: Optional[str]
    CLOUDINARY_CLOUD_NAME: Optional[str]
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
