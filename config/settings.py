from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from pathlib import Path



    


        


class SinopacSettings(BaseSettings):
    api_key: str = ""
    api_secret: str = ""
    simulation: bool = True
    cert_file: str = ""
    cert_pwd: str = ""
    person_id: str = ""

    model_config = ConfigDict(
        env_prefix="SINOPAC_"
    )
    def create_sdk(self):
        import shioaji as sj
        return sj.Shioaji(simulation=self.simulation)

class Settings(BaseSettings):
    app_name: str = "Golden Egg"
    egg_debug: bool = True
    
    model_config = ConfigDict(
        env_file=".env-debug",
        env_file_encoding = "utf-8"
    )



settings = Settings() 