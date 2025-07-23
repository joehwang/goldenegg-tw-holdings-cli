from pathlib import Path
from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from esun_trade.sdk import SDK
from esun_trade.order import OrderObject
from esun_trade.constant import (APCode, Trade, PriceFlag, BSFlag, Action)


class EsunSettings(BrokerSettings):
    config_file: str = ""

    model_config = ConfigDict(
        env_prefix="ESUN_"
    )

    def create_sdk(self):
        """建立玉山 SDK 實例"""
        from esun_trade.sdk import SDK
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "broker" / "esun" / self.config_file
        # 讀取設定檔
        config = ConfigParser()
        config.read(config_path)

        # 將憑證路徑轉換為絕對路徑
        if config.has_section('Cert') and config.has_option('Cert', 'Path'):
            cert_relative_path = config.get('Cert', 'Path')
            cert_absolute_path = project_root / "broker" / "esun" / cert_relative_path
            config.set('Cert', 'Path', str(cert_absolute_path))

        return SDK(config)

class EsunClient(BrokerClient):
    def load_settings(self) -> EsunSettings:
        env_file = EsunSettings.get_env_file("esun")
        return EsunSettings(_env_file=env_file)

    def get_holdings(self) -> str:
        # 使用 self.settings 來取得配置
        config_path = Path(__file__).parent / self.settings.config_file
        print(config_path)

        # 登入
        sdk = self.settings.create_sdk()
        #sdk = SDK(config)
        sdk.login()


        # 庫存明細
        inventories = sdk.get_inventories()
        print(inventories)
        return "yes get holdings"
