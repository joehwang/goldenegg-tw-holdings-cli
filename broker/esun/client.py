from pathlib import Path
from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from esun_trade.sdk import SDK
from esun_trade.order import OrderObject
from esun_trade.constant import (APCode, Trade, PriceFlag, BSFlag, Action)
from models.holdings import Holdings, Position
from models.accounts import Account
from typing import List, Dict, Any
from models.market_data import MarketDataProvider

class EsunSettings(BrokerSettings):
    config_file: str = ""

    model_config = ConfigDict(
        env_prefix="ESUN_"
    )

    def create_sdk(self):
        """建立玉山 SDK 實例"""
        from esun_trade.sdk import SDK
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "broker" / "esun" / "certs" / self.config_file
        # 讀取設定檔
        config = ConfigParser()
        config.read(config_path)

        # 將憑證路徑轉換為絕對路徑
        if config.has_section('Cert') and config.has_option('Cert', 'Path'):
            cert_relative_path = config.get('Cert', 'Path')
            cert_absolute_path = project_root / "broker" / "esun" / "certs" / cert_relative_path
            config.set('Cert', 'Path', str(cert_absolute_path))      
        return SDK(config)

class EsunClient(BrokerClient):
    def load_settings(self) -> EsunSettings:
        env_file = EsunSettings.get_env_file("esun")
        return EsunSettings(_env_file=env_file)

    def get_holdings(self) -> Holdings:
        """取得庫存明細並轉換為 Holdings 模型"""
        # 使用 self.settings 來取得配置
        config_path = Path(__file__).parent / self.settings.config_file
       
        # 登入
        sdk = self.settings.create_sdk()
        sdk.login()

        # 庫存明細
        inventories = sdk.get_inventories()
        
        # 取得帳戶資訊 (假設從 SDK 或設定中取得)
        account = Account(
            account_id="esun_account",  # 實際應從 SDK 取得
            broker_name="玉山證券"
        )
        
        # 轉換庫存資料為 Position 清單
        positions = self._convert_inventories_to_positions(inventories)
        
        return Holdings(
            account=account,
            positions=positions,
            data_source="api"
        )
    
    def _convert_inventories_to_positions(self, inventories: List[Dict[str, Any]]) -> List[Position]:
        """將玉山庫存資料轉換為 Position 清單"""
        positions = []
        
        for inventory in inventories:
            # 取得基本資訊
            symbol = inventory.get("stk_no", "")
            name = inventory.get("stk_na", "")
            avg_cost = float(inventory.get("price_avg", 0))
            
            # 從 stk_dats 中取得詳細資訊（通常只有一筆或合併後的資料）
            stk_dats = inventory.get("stk_dats", [])
            if stk_dats:
                # 取第一筆資料（或合併後的資料）
                first_dat = stk_dats[0]
                quantity = int(first_dat.get("qty", 0))
                
                             
                current_price = MarketDataProvider().get_current_price(symbol)
        
            else:
                quantity = 0
                current_price = None
            
            position = Position(
                symbol=symbol,
                quantity=quantity,
                avg_cost=avg_cost,
                current_price=current_price,
                broker_code="esun",
                broker_name="玉山證券"
            )
            positions.append(position)
            
        return positions
