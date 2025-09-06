import shioaji as sj
import sys
from config.settings import settings, BaseSettings
from pathlib import Path
from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from models.holdings import Holdings, Position
from models.accounts import Account
from typing import List

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

    def get_holdings(self) -> Holdings:
        """取得持股資訊，回傳標準 Holdings 格式"""
        # 取得永豐金設定
        sinopac_settings = self.load_settings()

        # 建立 API 實例
        api = sj.Shioaji(simulation=sinopac_settings.simulation)
        
        # 登入
        accounts = api.login(sinopac_settings.api_key, sinopac_settings.api_secret)
        
        # 查詢帳號列表
        account_list = api.list_accounts()
        
        if not account_list:
            raise Exception("找不到永豐帳戶")
        
        # 使用第一個帳戶
        account = account_list[0]
        
        # 取得持股明細
        stock_positions = api.list_positions(
            account, unit=sj.constant.Unit.Share)
        
        # 啟用憑證（如果需要）
        try:
            api.activate_ca(
                ca_path=str(Path(__file__).parent / "certs"/ sinopac_settings.cert_file),
                ca_passwd=sinopac_settings.cert_pwd,
                person_id=sinopac_settings.person_id,
            )
            print("憑證啟用成功")
        except Exception as e:
            print(f"憑證啟用失敗: {e}")
        
        # 建立帳戶資訊
        account_info = Account(
            account_id=account.account_id,  # 永豐使用 account_id 而不是 account
            branch_no=getattr(account, 'branch_id', None),
            broker_name="永豐證券"
        )
        
        # 轉換持股資料為 Position 列表（只包含真正持有的股票）
        positions = [
            self._convert_stock_position_to_position(stock_pos) 
            for stock_pos in stock_positions 
            if stock_pos.quantity > 0  # 只轉換真正持有的股票
        ]
        
        return Holdings(
            account=account_info,
            positions=positions,
            data_source="api"
        )
    
    def _convert_stock_position_to_position(self, stock_pos) -> Position:
        """轉換永豐 StockPosition 資料為標準 Position 格式"""
        return Position(
            symbol=stock_pos.code,
            quantity=stock_pos.quantity,
            available_quantity=stock_pos.quantity,  # 假設全部可交易
            avg_cost=stock_pos.price,
            current_price=stock_pos.last_price,
            broker_code="sinopac",
            broker_name="永豐證券"
        )
