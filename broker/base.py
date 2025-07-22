from abc import ABC, abstractmethod
from pathlib import Path
from pydantic_settings import BaseSettings

class BrokerSettings(BaseSettings):

    @classmethod
    def get_env_file(cls,broker_name :str,is_test: bool = False) -> str:
        env_file=".env.test" if is_test else ".env"
        broker_dir=Path(__file__).parent / broker_name
        return str(broker_dir / env_file)

class BrokerClient(ABC):
    def __init__(self,is_test:bool=False):
        self.is_test=is_test
        self.settings=self.load_settings()


    @abstractmethod
    def load_settings(self) -> BrokerSettings:
        """載入卷商設定"""
        pass

