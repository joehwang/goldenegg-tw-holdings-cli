from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from pathlib import Path
from configparser import ConfigParser
from masterlink_sdk import MasterlinkSDK, Order, TimeInForce, OrderType, PriceType, MarketType, BSAction

class MasterlinkSettings(BrokerSettings):
    login_id: str = ""
    login_pwd: str = ""
    cert_file: str = ""
    cert_pwd: str = ""
    model_config = ConfigDict(
        env_prefix="MASTERLINK_"
    )

    def create_sdk(self):
        from masterlink_sdk import MasterlinkSDK    
        project_root = Path(__file__).parent.parent.parent
        self.cert_file = str(project_root / "broker" / "masterlink" / self.cert_file)
      
        return MasterlinkSDK()

class MasterlinkClient(BrokerClient):
    def load_settings(self) -> MasterlinkSettings:
        env_file = MasterlinkSettings.get_env_file("masterlink")
        return MasterlinkSettings(_env_file=env_file)

    def get_holdings(self) -> str:
        sdk = self.settings.create_sdk()

        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd,
                            self.settings.cert_file, self.settings.cert_pwd)
        acc = accounts[0]
        print(sdk.accounting.inventories(acc))
        return "ok"
