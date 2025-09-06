from abc import ABC, abstractmethod
from pathlib import Path
from pydantic_settings import BaseSettings
from config.settings import settings
class BrokerSettings(BaseSettings):

    @classmethod
    def get_env_file(cls,broker_name :str) -> str:
        env_file=".env.test" if settings.egg_debug else ".env"
        broker_dir=Path(__file__).parent / broker_name
        return str(broker_dir / env_file)

class BrokerClient(ABC):
    def __init__(self):
        self.is_test=settings.egg_debug
        self.settings=self.load_settings()


    @abstractmethod
    def load_settings(self) -> BrokerSettings:
        """載入卷商設定"""
        pass

