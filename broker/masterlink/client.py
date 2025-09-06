from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from pathlib import Path
from configparser import ConfigParser
from masterlink_sdk import MasterlinkSDK, Order, TimeInForce, OrderType, PriceType, MarketType, BSAction
from models.holdings import Holdings, Position
from models.accounts import Account
from typing import List

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
        self.cert_file = str(project_root / "broker" / "masterlink" / "certs" / self.cert_file)
      
        return MasterlinkSDK()

class MasterlinkClient(BrokerClient):
    def load_settings(self) -> MasterlinkSettings:
        env_file = MasterlinkSettings.get_env_file("masterlink")
        return MasterlinkSettings(_env_file=env_file)

    def get_holdings(self) -> Holdings:
        """取得持股資訊，回傳標準 Holdings 格式"""
        sdk = self.settings.create_sdk()

        # 登入並取得帳戶
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd,
                            self.settings.cert_file, self.settings.cert_pwd)
        
        if not accounts:
            raise Exception("找不到元富帳戶")
            
        acc = accounts[0]
        
        # 取得庫存資料
        inventories_result = sdk.accounting.inventories(acc)
        
        # 建立帳戶資訊
        account_info = Account(
            account_id=acc.account,
            branch_no=acc.branch_name,
            broker_name="元富證券"
        )
        
        # 轉換庫存資料為 Position 列表
        positions = [
            self._convert_position_summary_to_position(position_summary)
            for position_summary in inventories_result.position_summaries
            if int(position_summary.current_quantity) > 0  # 只包含有持股的
        ]
        
        return Holdings(
            account=account_info,
            positions=positions,
            data_source="api"
        )
    
    def _convert_position_summary_to_position(self, position_summary) -> Position:
        """轉換元富 PositionSummary 資料為標準 Position 格式"""
        return Position(
            symbol=position_summary.symbol,
            quantity=int(position_summary.current_quantity),
            available_quantity=int(position_summary.current_quantity),  # 假設全部可交易
            avg_cost=float(position_summary.average_price),
            current_price=float(position_summary.current_price),
            broker_code="masterlink",
            broker_name="元富證券"

        )
