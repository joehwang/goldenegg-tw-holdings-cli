from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from pathlib import Path


class EsunSettings(BaseSettings):
    config_file: str = ""
    model_config = ConfigDict(
        env_prefix="ESUN_"
    )

    def create_sdk(self):
        """建立玉山 SDK 實例"""
        from esun_trade.sdk import SDK
        project_root = Path(__file__).parent.parent
        config_path = project_root / "borker" / "esun" / self.config_file
        # 讀取設定檔
        config = ConfigParser()
        config.read(config_path)

        # 將憑證路徑轉換為絕對路徑
        if config.has_section('Cert') and config.has_option('Cert', 'Path'):
            cert_relative_path = config.get('Cert', 'Path')
            cert_absolute_path = project_root / "borker" / "esun" / cert_relative_path
            config.set('Cert', 'Path', str(cert_absolute_path))

        return SDK(config)
    

class FubonSettings(BaseSettings):
    login_id: str=""
    login_pwd: str=""
    cert_file: str=""
    cert_pwd: str=""
    login_url: str=""
    model_config = ConfigDict(
        env_prefix="FUBON_"
    )
    def create_sdk(self):
        """建立富邦 SDK 實例"""
        from fubon_neo.sdk import FubonSDK
       
        if self.login_url != "":
            return FubonSDK(30, 2, url=self.login_url)
        else:
            return FubonSDK()
        
class MasterlinkSettings(BaseSettings):
    login_id: str = ""
    login_pwd: str = ""
    cert_file: str = ""
    cert_pwd: str = ""
    model_config = ConfigDict(
        env_prefix="MASTERLINK_"
    )

    def create_sdk(self):
        from masterlink_sdk import MasterlinkSDK
        return MasterlinkSDK()

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

    def get_esun_settings(self) -> EsunSettings:
        """動態載入玉山證券設定"""
        # 步驟 1: 根據 debug 狀態選擇檔案
        if self.egg_debug:
            env_file = "borker/esun/.env.test"      
        else:
            env_file = "borker/esun/.env"  
        
        return EsunSettings(_env_file=env_file)
    
    def get_fubon_settings(self) -> FubonSettings:
        """動態載入富邦證券設定"""

        if self.egg_debug:
            env_file = "borker/fubon/.env.test"      
        else:
            env_file = "borker/fubon/.env"  
        return FubonSettings(_env_file=env_file)

    def get_masterlink_settings(self) -> MasterlinkSettings:
        """動態載入元富證券設定"""
        if self.egg_debug:
            env_file = "borker/masterlink/.env.test"      
        else:
            env_file = "borker/masterlink/.env"  
        return MasterlinkSettings(_env_file=env_file)

    def get_sinopac_settings(self) -> SinopacSettings:
        """動態載入永豐金證券設定"""
        if self.egg_debug:
            env_file = "borker/sinopac/.env.test"      
        else:
            env_file = "borker/sinopac/.env"
        return SinopacSettings(_env_file=env_file)


settings = Settings() 