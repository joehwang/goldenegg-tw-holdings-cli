from pathlib import Path
from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from fubon_neo.sdk import FubonSDK, Order
from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction


class FubonSettings(BrokerSettings):
    login_id: str = ""
    login_pwd: str = ""
    cert_file: str = ""
    cert_pwd: str = ""
    login_url: str = ""
    cert_path: str = ""
    model_config = ConfigDict(
        env_prefix="FUBON_"
    )

    def create_sdk(self):
        """建立富邦 SDK 實例"""
        from fubon_neo.sdk import FubonSDK
        self.cert_path = Path(__file__).parent.parent.parent / "broker" / "fubon"
        if self.login_url != "":
            return FubonSDK(30, 2, url=self.login_url)
        else:
            return FubonSDK()


class FubonClient(BrokerClient):
    def load_settings(self) -> FubonSettings:
        env_file = FubonSettings.get_env_file("fubon")
        return FubonSettings(_env_file=env_file)

    def get_holdings(self) -> str:

        sdk = self.settings.create_sdk()

        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd,
                            f"{self.settings.cert_path}/{self.settings.cert_file}", self.settings.cert_pwd)
        acc = accounts.data[0]
        
        # 取得庫存
        result = sdk.accounting.inventories(acc)
        print(result)
        return "yes get holdings"
