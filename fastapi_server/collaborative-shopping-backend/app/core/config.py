from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):

    app_name: str = "E-commerce API"
    app_version: str = "1.0.0"
    environment: str = "development"
    

    database_url: str = "postgresql://admin:admin@localhost:5432/ecom"
    

    secret_key: str = "SecretKey" #TODO
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    

    api_v1_prefix: str = "/api/v1"
    allowed_hosts: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()