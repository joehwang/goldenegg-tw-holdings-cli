import shioaji as sj
import sys
from config.settings import settings, BaseSettings
from pathlib import Path
from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from configparser import ConfigParser

class SinopacSettings(BrokerSettings):
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


class SinopacClient(BrokerClient):
    def load_settings(self) -> SinopacSettings:
        env_file = SinopacSettings.get_env_file("sinopac")
        return SinopacSettings(_env_file=env_file)

    def get_holdings(self) -> str:
        sdk = self.settings.create_sdk()


        # 將專案根目錄加入 Python 路徑
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))


        # 取得永豐金設定
        sinopac_settings = self.load_settings()
        print(sinopac_settings)

        # 建立 API 實例
        api = sj.Shioaji(simulation=sinopac_settings.simulation)
        print(sinopac_settings)
        # 登入
        accounts = api.login(sinopac_settings.api_key, sinopac_settings.api_secret)
        print(accounts)

        # 查詢帳號列表
        account_list = api.list_accounts()
        print(account_list)

        result = api.activate_ca(
            ca_path=str(Path(__file__).parent / sinopac_settings.cert_file),
            ca_passwd=sinopac_settings.cert_pwd,
            person_id=sinopac_settings.person_id,
        )
        return account_list
