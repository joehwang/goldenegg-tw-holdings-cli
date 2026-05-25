import unittest
import os
from pathlib import Path
from broker.fubon.client import FubonClient, FubonSettings
from integration.helpers import get_holdings_or_skip
from models.holdings import Holdings, Position
from models.accounts import Account


class TestFubonIntegration(unittest.TestCase):
    """富邦證券整合測試 - 需要真實的帳號設定"""
    
    def setUp(self):
        """測試前檢查環境設定"""
        # 檢查是否有富邦的環境檔案
        fubon_env_path = Path(__file__).parent.parent.parent / "broker" / "fubon" / ".env"
        if not fubon_env_path.exists():
            self.skipTest("找不到富邦環境設定檔，跳過整合測試")
        
        # 嘗試建立 FubonSettings 來載入環境變數
        try:
            settings = FubonSettings(_env_file=str(fubon_env_path))
            
            # 檢查必要的設定
            if not settings.login_id:
                self.skipTest("缺少 FUBON_LOGIN_ID 設定")
            if not settings.api_key:
                self.skipTest("缺少 FUBON_API_KEY 設定")
            if not settings.cert_file:
                self.skipTest("缺少 FUBON_CERT_FILE 設定")
                
            print(f"✅ 環境設定檢查通過，帳號: {settings.login_id}")
            
        except Exception as e:
            self.skipTest(f"載入環境設定失敗: {e}")
    
    def test_fubon_client_real_connection(self):
        """測試富邦客戶端真實連線"""
        try:
            client = FubonClient()
            self.assertIsInstance(client, FubonClient)
            print(f"✅ 富邦客戶端建立成功")
            
        except Exception as e:
            self.fail(f"富邦客戶端建立失敗: {e}")
    
    def test_fubon_get_holdings_real_api(self):
        """測試富邦取得真實持股資料"""
        try:
            holdings = get_holdings_or_skip(self, FubonClient, "富邦")
            
            # 驗證回傳類型
            self.assertIsInstance(holdings, Holdings)
            self.assertIsInstance(holdings.account, Account)
            
            # 驗證帳戶資訊
            self.assertEqual(holdings.account.broker_name, "富邦證券")
            self.assertIsNotNone(holdings.account.account_id)
            
            # 驗證持股資料結構
            self.assertIsInstance(holdings.positions, list)
            
            # 如果有持股，驗證 Position 物件
            if holdings.positions:
                for position in holdings.positions:
                    self.assertIsInstance(position, Position)
                    self.assertIsNotNone(position.symbol)
                    self.assertGreaterEqual(position.quantity, 0)
                    
                    print(f"持股: {position.stock_name}({position.symbol}), 數量: {position.quantity} 現價: {position.current_price}")
            
            # 驗證計算欄位
            self.assertIsInstance(holdings.total_cost_value, float)
            self.assertIsInstance(holdings.total_market_value, float)
            
            print(f"✅ 成功取得持股資料")
            print(f"帳戶: {holdings.account.account_id}")
            print(f"持股數量: {len(holdings.positions)}")
            print(f"總成本: {holdings.total_cost_value}")
            print(f"總市值: {holdings.total_market_value}")
            
        except unittest.SkipTest:
            raise
        except Exception as e:
            self.fail(f"取得富邦持股失敗: {e}")
    

    



if __name__ == '__main__':
    # 執行整合測試時顯示詳細輸出
    unittest.main(verbosity=2)
