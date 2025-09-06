from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # 根據實際目錄調整
ENV_PATH = PROJECT_ROOT / ".env-debug"
class Settings(BaseSettings):
    app_name: str = "Golden Egg"
    egg_debug: bool = True
    
    model_config = ConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding = "utf-8"
    )

settings = Settings() 