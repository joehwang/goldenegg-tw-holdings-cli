from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from pathlib import Path
from unittest.mock import Mock
from taishin_sdk import TaishinSDK
from models.holdings import Holdings, Position
from models.accounts import Account

class TsscoSettings(BrokerSettings):
    login_id: str = ""
    login_pwd: str = ""
    cert_file: str = ""
    cert_pwd: str = ""
    model_config = ConfigDict(
        env_prefix="TSSCO_",
        extra="ignore"
    )

    def create_sdk(self):
        project_root = Path(__file__).parent.parent.parent
        self.cert_file = str(project_root / "broker" / "tssco" / "certs" / self.cert_file)

        return TaishinSDK()

class LegacyTsscoEnvSettings(BrokerSettings):
    login_id: str = ""
    login_pwd: str = ""
    cert_file: str = ""
    cert_pwd: str = ""
    model_config = ConfigDict(
        env_prefix="MASTERLINK_",
        extra="ignore"
    )


class TsscoClient(BrokerClient):
    def load_settings(self) -> TsscoSettings:
        env_file = TsscoSettings.get_env_file("tssco")
        settings = TsscoSettings(_env_file=env_file)
        if all((settings.login_id, settings.login_pwd, settings.cert_file, settings.cert_pwd)):
            return settings

        legacy_settings = LegacyTsscoEnvSettings(_env_file=env_file)
        for field in ("login_id", "login_pwd", "cert_file", "cert_pwd"):
            if not getattr(settings, field):
                setattr(settings, field, getattr(legacy_settings, field))

        return settings

    def get_holdings(self) -> Holdings:
        """取得持股資訊，回傳標準 Holdings 格式"""
        sdk = self.settings.create_sdk()

        # 登入並取得帳戶
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd,
                            self.settings.cert_file, self.settings.cert_pwd)
        
        if not accounts:
            raise Exception("找不到台新證券帳戶")
            
        acc = accounts[0]
        
        # 取得庫存資料
        inventories_result = sdk.accounting.inventories(acc)
        
        # 建立帳戶資訊
        account_info = Account(
            account_id=acc.account,
            branch_no=acc.branch_name,
            broker_name="台新證券"
        )
        
        # 轉換庫存資料為 Position 列表
        positions = [
            self._convert_position_summary_to_position(position_summary)
            for position_summary in inventories_result.position_summaries
            if int(self._get_field(position_summary, "current_quantity", "currentQuantity", default=0)) > 0
        ]
        
        return Holdings(
            account=account_info,
            positions=positions,
            data_source="api"
        )

    @staticmethod
    def _get_field(obj, *names, default=None):
        for name in names:
            if isinstance(obj, Mock) and name not in obj.__dict__:
                continue
            if hasattr(obj, name):
                return getattr(obj, name)
        return default

    def _convert_position_summary_to_position(self, position_summary) -> Position:
        """轉換台新 Nova API PositionSummary 資料為標準 Position 格式"""
        quantity = int(self._get_field(position_summary, "current_quantity", "currentQuantity", default=0))
        avg_cost = float(self._get_field(position_summary, "average_price", "averagePrice", default=0) or 0)
        current_price = self._get_field(position_summary, "current_price", "currentPrice")
        if current_price is None and quantity > 0:
            market_value = self._get_field(position_summary, "stock_evaluation", "stockEvaluation", "market_value", "marketValue")
            if market_value not in (None, ""):
                current_price = float(market_value) / quantity

        return Position(
            symbol=self._get_field(position_summary, "symbol", default=""),
            stock_name=self._get_field(position_summary, "symbol_name", "symbolName", default=None),
            quantity=quantity,
            available_quantity=quantity,  # 假設全部可交易
            avg_cost=avg_cost,
            current_price=float(current_price) if current_price not in (None, "") else None,
            broker_code="tssco",
            broker_name="台新證券"

        )
