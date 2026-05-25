from pathlib import Path
from broker.base import BrokerClient, BrokerSettings
from pydantic import ConfigDict
from configparser import ConfigParser
from fubon_neo.sdk import FubonSDK, Order
from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction
from models.holdings import Holdings, Position
from models.accounts import Account
from typing import List
from models.market_data import MarketDataProvider
import urllib3
# 禁用 SSL 警告
 
class FubonSettings(BrokerSettings):
    login_id: str = ""
    api_key: str = ""
    cert_file: str = ""
    cert_pwd: str = ""
    login_url: str = ""
    cert_path: str = ""
    model_config = ConfigDict(
        env_prefix="FUBON_",
        extra="ignore",
    )

    def create_sdk(self):
        """建立富邦 SDK 實例"""
        from fubon_neo.sdk import FubonSDK
        self.cert_path = Path(__file__).parent.parent.parent / "broker" / "fubon" / "certs"
        if self.login_url != "":
            return FubonSDK(30, 2, url=self.login_url)
        else:
            return FubonSDK()


class FubonClient(BrokerClient):
    def load_settings(self) -> FubonSettings:
        env_file = FubonSettings.get_env_file("fubon")
        return FubonSettings(_env_file=env_file)

    def _validate_login_result(self, accounts):
        """Validate Fubon login response and return the first account."""
        if accounts is None:
            raise RuntimeError("富邦登入失敗: SDK 未回傳登入結果")

        is_success = getattr(accounts, "is_success", None)
        if is_success is False:
            message = getattr(accounts, "message", "無錯誤訊息")
            code = getattr(accounts, "code", None)
            code_text = f" code={code}," if code is not None else ""
            raise RuntimeError(f"富邦登入失敗:{code_text} message={message}")

        account_data = getattr(accounts, "data", None)
        if not account_data:
            message = getattr(accounts, "message", "無錯誤訊息")
            code = getattr(accounts, "code", None)
            code_text = f" code={code}," if code is not None else ""
            raise RuntimeError(f"富邦登入成功但沒有帳戶資料:{code_text} message={message}")

        return account_data[0]

    def get_holdings(self) -> Holdings:
        """取得持股資訊，回傳標準 Holdings 格式"""
        sdk = self.settings.create_sdk()
        cert_path = f"{self.settings.cert_path}/{self.settings.cert_file}"
        if not self.settings.api_key:
            raise RuntimeError("缺少 FUBON_API_KEY 設定")

        accounts = sdk.apikey_login(
            self.settings.login_id,
            self.settings.api_key,
            cert_path,
            self.settings.cert_pwd or self.settings.login_id,
        )
        acc = self._validate_login_result(accounts)
        
        # 取得庫存
        result = sdk.accounting.inventories(acc)
        # 取得未實現損益 / 平均價格
        unrealized_pnl = sdk.accounting.unrealized_gains_and_loses(acc)
   
        if not result.is_success:
            raise Exception(f"取得富邦庫存失敗: {result.message}")


        # 把result.data和unrealized_pnl.data合併
        merge_inventory_data = []
        for inventory in result.data:
            # 手動提取 inventory 物件的屬性
            inventory_dict = {
                'stock_no': inventory.stock_no,
                'today_qty': inventory.today_qty,
                'tradable_qty': inventory.tradable_qty,
                'odd': {
                    'today_qty': inventory.odd.today_qty,
                    'tradable_qty': inventory.odd.tradable_qty,
                }
            }

            # 在 unrealized_pnl.data 列表中找到對應的股票資料
            unrealized_dict = {'cost_price': 0.0,
                            'unrealized_profit': 0, 'unrealized_loss': 0}

            for unrealized_item in unrealized_pnl.data:
                if unrealized_item.stock_no == inventory.stock_no:
                    unrealized_dict = {
                        'cost_price': unrealized_item.cost_price,
                        'unrealized_profit': getattr(unrealized_item, 'unrealized_profit', 0),
                        'unrealized_loss': getattr(unrealized_item, 'unrealized_loss', 0),
                    }
                    break  # 找到就跳出迴圈

            # 合併字典
            merged_item = {**inventory_dict, **unrealized_dict}
            merge_inventory_data.append(merged_item)

        # 建立帳戶資訊
        account_info = Account(
            account_id=acc.account,
            branch_no=getattr(acc, 'branch_no', None),
            broker_name="富邦證券"
        )
    
        # 轉換庫存資料為 Position 列表
        positions = [self._convert_inventory_to_position(inventory) 
                    for inventory in merge_inventory_data]
    
        return Holdings(
            account=account_info,
            positions=positions,
            data_source="api"
        )
    
    def _convert_inventory_to_position(self, inventory) -> Position:
        """轉換富邦 Inventory 資料為標準 Position 格式"""
        # 計算總持股數量（整股 + 零股）
        # {'stock_no': '5306', 'today_qty': 2000, 'tradable_qty': 2000, 'odd': {'today_qty': 100, 'tradable_qty': 100}, 'cost_price': 158.2905, 'unrealized_profit': 0, 'unrealized_loss': 132327}
        total_quantity = inventory["today_qty"] + inventory["odd"]["today_qty"]
        total_available = inventory["tradable_qty"] + inventory["odd"]["tradable_qty"]
        return Position(
            symbol=inventory["stock_no"],

            quantity=total_quantity,
            available_quantity=total_available,
            avg_cost=inventory["cost_price"],  # 富邦庫存 API 不提供平均成本，需要另外查詢
            current_price=MarketDataProvider().get_current_price(
                inventory["stock_no"]),
            broker_code="fubon",
            broker_name="富邦證券"
        )
