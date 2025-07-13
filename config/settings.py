from pydantic_settings import BaseSettings

class EsunSettings(BaseSettings):
    config: str=""
    class Config:
        env_prefix = "ESUN_"
        env_file = "borker/esun/.env"  

class FubonSettings(BaseSettings):
    login_id: str=""
    login_pwd: str=""
    cert_path: str=""
    cert_pwd: str=""
    
    class Config:
        env_prefix = "FUBON_"
        env_file = "borker/fubon/.env"  

class Settings(BaseSettings):
    app_name: str = "Golden Egg"
    debug: bool = False
    
    
    class Config:
        env_file = ".env"  
        env_file_encoding = "utf-8"

    def get_esun_settings(self) -> EsunSettings:
        """動態載入玉山證券設定"""
        # 步驟 1: 根據 debug 狀態選擇檔案
        if self.debug:
            env_file = "borker/esun/.env.test"      
        else:
            env_file = "borker/esun/.env"  
        
        return EsunSettings(_env_file=env_file)
    
    def get_fubon_settings(self) -> FubonSettings:
        """動態載入富邦證券設定"""
        if self.debug:
            env_file = "borker/fubon/.env.test"      
        else:
            env_file = "borker/fubon/.env"  
        return FubonSettings(_env_file=env_file)
settings = Settings() 