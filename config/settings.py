from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Golden Egg"
    egg_debug: bool = True
    
    model_config = ConfigDict(
        env_file=".env-debug",
        env_file_encoding = "utf-8"
    )

settings = Settings() 