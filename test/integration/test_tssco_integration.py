import unittest
from pathlib import Path
from broker.tssco.client import TsscoClient
from integration.helpers import get_holdings_or_skip
from models.holdings import Holdings, Position
from models.accounts import Account


class TestTsscoIntegration(unittest.TestCase):
    """台新證券 Nova API 整合測試 - 需要真實的帳號設定"""
    
    def setUp(self):
        """測試前檢查環境設定"""
        # 檢查是否有台新證券 Nova API 的環境檔案
        tssco_env_path = Path(__file__).parent.parent.parent / "broker" / "tssco" / ".env"
        if not tssco_env_path.exists():
            self.skipTest("找不到台新證券環境設定檔，跳過整合測試")
        
        # 嘗試建立 TsscoSettings 來載入環境變數
        try:
            client = TsscoClient()
            settings = client.settings
            
            # 檢查必要的設定
            if not settings.login_id:
                self.skipTest("缺少 TSSCO_LOGIN_ID 設定")
            if not settings.login_pwd:
                self.skipTest("缺少 TSSCO_LOGIN_PWD 設定")
            if not settings.cert_file:
                self.skipTest("缺少 TSSCO_CERT_FILE 設定")
            if not settings.cert_pwd:
                self.skipTest("缺少 TSSCO_CERT_PWD 設定")
                
            print("✅ 環境設定檢查通過")
            
        except Exception as e:
            self.skipTest(f"載入環境設定失敗: {e}")
    
    def test_tssco_client_real_connection(self):
        """測試台新證券客戶端真實連線"""
        try:
            client = TsscoClient()
            self.assertIsInstance(client, TsscoClient)
            print(f"✅ 台新證券客戶端建立成功")
            
        except Exception as e:
            self.fail(f"台新證券客戶端建立失敗: {e}")
    
    def test_tssco_get_holdings_real_api(self):
        """測試台新證券取得真實持股資料"""
        try:
            holdings = get_holdings_or_skip(self, TsscoClient, "台新證券")
            
            # 驗證回傳類型
            self.assertIsInstance(holdings, Holdings)
            self.assertIsInstance(holdings.account, Account)
            
            # 驗證帳戶資訊
            self.assertEqual(holdings.account.broker_name, "台新證券")
            self.assertIsNotNone(holdings.account.account_id)
            
            # 驗證持股資料結構
            self.assertIsInstance(holdings.positions, list)
            
            # 如果有持股，驗證 Position 物件
            if holdings.positions:
                for position in holdings.positions:
                    self.assertIsInstance(position, Position)
                    self.assertIsNotNone(position.symbol)
                    self.assertGreaterEqual(position.quantity, 0)
                    
            # 驗證計算欄位
            self.assertIsInstance(holdings.total_cost_value, float)
            self.assertIsInstance(holdings.total_market_value, float)
            
            print(f"✅ 成功取得持股資料")
            print(f"持股數量: {len(holdings.positions)}")
            
        except unittest.SkipTest:
            raise
        except Exception as e:
            self.fail(f"取得台新證券持股失敗: {e}")
    
    def test_tssco_data_consistency(self):
        """測試台新證券資料一致性"""
        try:
            # 連續呼叫兩次，檢查資料一致性
            holdings1 = get_holdings_or_skip(self, TsscoClient, "台新證券")
            holdings2 = get_holdings_or_skip(self, TsscoClient, "台新證券")
            
            # 帳戶資訊應該相同
            self.assertEqual(holdings1.account.account_id, holdings2.account.account_id)
            self.assertEqual(holdings1.account.broker_name, holdings2.account.broker_name)
            
            # 持股數量應該相同（假設短時間內沒有交易）
            self.assertEqual(len(holdings1.positions), len(holdings2.positions))
            
            print(f"✅ 資料一致性測試通過")
            
        except unittest.SkipTest:
            raise
        except Exception as e:
            self.fail(f"資料一致性測試失敗: {e}")


if __name__ == '__main__':
    # 執行整合測試時顯示詳細輸出
    unittest.main(verbosity=2)
