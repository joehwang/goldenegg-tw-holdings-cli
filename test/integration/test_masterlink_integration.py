import unittest
import os
from pathlib import Path
from broker.masterlink.client import MasterlinkClient, MasterlinkSettings
from models.holdings import Holdings, Position
from models.accounts import Account


class TestMasterlinkIntegration(unittest.TestCase):
    """元富證券整合測試 - 需要真實的帳號設定"""
    
    def setUp(self):
        """測試前檢查環境設定"""
        # 檢查是否有元富的環境檔案
        masterlink_env_path = Path(__file__).parent.parent.parent / "broker" / "masterlink" / ".env"
        if not masterlink_env_path.exists():
            self.skipTest("找不到元富環境設定檔，跳過整合測試")
        
        # 嘗試建立 MasterlinkSettings 來載入環境變數
        try:
            settings = MasterlinkSettings(_env_file=str(masterlink_env_path))
            
            # 檢查必要的設定
            if not settings.login_id:
                self.skipTest("缺少 MASTERLINK_LOGIN_ID 設定")
            if not settings.login_pwd:
                self.skipTest("缺少 MASTERLINK_LOGIN_PWD 設定")
            if not settings.cert_file:
                self.skipTest("缺少 MASTERLINK_CERT_FILE 設定")
            if not settings.cert_pwd:
                self.skipTest("缺少 MASTERLINK_CERT_PWD 設定")
                
            print(f"✅ 環境設定檢查通過，帳號: {settings.login_id}")
            
        except Exception as e:
            self.skipTest(f"載入環境設定失敗: {e}")
    
    def test_masterlink_client_real_connection(self):
        """測試元富客戶端真實連線"""
        try:
            client = MasterlinkClient()
            self.assertIsInstance(client, MasterlinkClient)
            print(f"✅ 元富客戶端建立成功")
            
        except Exception as e:
            self.fail(f"元富客戶端建立失敗: {e}")
    
    def test_masterlink_get_holdings_real_api(self):
        """測試元富取得真實持股資料"""
        try:
            client = MasterlinkClient()
            holdings = client.get_holdings()
            
            # 驗證回傳類型
            self.assertIsInstance(holdings, Holdings)
            self.assertIsInstance(holdings.account, Account)
            
            # 驗證帳戶資訊
            self.assertEqual(holdings.account.broker_name, "元富證券")
            self.assertIsNotNone(holdings.account.account_id)
            
            # 驗證持股資料結構
            self.assertIsInstance(holdings.positions, list)
            
            # 如果有持股，驗證 Position 物件
            if holdings.positions:
                for position in holdings.positions:
                    self.assertIsInstance(position, Position)
                    self.assertIsNotNone(position.symbol)
                    self.assertGreaterEqual(position.quantity, 0)
                    
                    print(
                        f"持股: {position.stock_name}({position.symbol}), 數量: {position.quantity} 現價: {position.current_price}")
            
            # 驗證計算欄位
            self.assertIsInstance(holdings.total_cost_value, float)
            self.assertIsInstance(holdings.total_market_value, float)
            
            print(f"✅ 成功取得持股資料")
            print(f"帳戶: {holdings.account.account_id}")
            print(f"持股數量: {len(holdings.positions)}")
            print(f"總成本: {holdings.total_cost_value}")
            print(f"總市值: {holdings.total_market_value}")
            
        except Exception as e:
            self.fail(f"取得元富持股失敗: {e}")
    
    def test_masterlink_data_consistency(self):
        """測試元富資料一致性"""
        try:
            client = MasterlinkClient()
            
            # 連續呼叫兩次，檢查資料一致性
            holdings1 = client.get_holdings()
            holdings2 = client.get_holdings()
            
            # 帳戶資訊應該相同
            self.assertEqual(holdings1.account.account_id, holdings2.account.account_id)
            self.assertEqual(holdings1.account.broker_name, holdings2.account.broker_name)
            
            # 持股數量應該相同（假設短時間內沒有交易）
            self.assertEqual(len(holdings1.positions), len(holdings2.positions))
            
            print(f"✅ 資料一致性測試通過")
            
        except Exception as e:
            self.fail(f"資料一致性測試失敗: {e}")


if __name__ == '__main__':
    # 執行整合測試時顯示詳細輸出
    unittest.main(verbosity=2)
