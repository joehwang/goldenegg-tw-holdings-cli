import unittest
import os
from pathlib import Path
from broker.esun.client import EsunClient, EsunSettings
from models.holdings import Holdings, Position
from models.accounts import Account

os.environ.setdefault(
    "PYTHON_KEYRING_BACKEND",
    "keyrings.cryptfile.cryptfile.CryptFileKeyring",
)
class TestEsunIntegration(unittest.TestCase):
    """玉山證券整合測試 - 需要真實的帳號設定"""
    
    def setUp(self):
        """測試前檢查環境設定"""
        # 檢查是否有玉山的環境檔案
        esun_env_path = Path(__file__).parent.parent.parent / "broker" / "esun" / ".env"
        if not esun_env_path.exists():
            self.skipTest("找不到玉山環境設定檔，跳過整合測試")
        
        # 嘗試建立 EsunSettings 來載入環境變數
        try:
            settings = EsunSettings(_env_file=str(esun_env_path))
            
            # 檢查必要的設定
            if not settings.config_file:
                self.skipTest("缺少 ESUN_CONFIG_FILE 設定")
                
            # 檢查設定檔是否存在
            config_path = Path(__file__).parent.parent.parent / "broker" / "esun" / "certs" / settings.config_file
            if not config_path.exists():
                self.skipTest(f"找不到玉山設定檔: {config_path}")
                
            print(f"✅ 環境設定檢查通過，設定檔: {settings.config_file}")
            
        except Exception as e:
            self.skipTest(f"載入環境設定失敗: {e}")
    
    def test_esun_client_real_connection(self):
        """測試玉山客戶端真實連線"""
        try:
            client = EsunClient()
            self.assertIsInstance(client, EsunClient)
            self.assertIsInstance(client.settings, EsunSettings)
            print(f"✅ 玉山客戶端建立成功")
            
        except Exception as e:
            self.fail(f"玉山客戶端建立失敗: {e}")
    
    def test_esun_get_holdings_real_api(self):
        """測試玉山取得真實持股資料"""
        try:
            client = EsunClient()
            holdings = client.get_holdings()
            
            # 驗證回傳類型
            self.assertIsInstance(holdings, Holdings)
            self.assertIsInstance(holdings.account, Account)
            
            # 驗證帳戶資訊
            self.assertEqual(holdings.account.broker_name, "玉山證券")
            self.assertIsNotNone(holdings.account.account_id)
            
            # 驗證持股資料結構
            self.assertIsInstance(holdings.positions, list)
            
            # 如果有持股，驗證 Position 物件
            if holdings.positions:
                for position in holdings.positions:
                    self.assertIsInstance(position, Position)
                    self.assertIsNotNone(position.symbol)
                    self.assertIsNotNone(position.stock_name)
                    self.assertGreaterEqual(position.quantity, 0)
                    self.assertGreater(position.avg_cost, 0)
                    
                    print(
                        f"持股: {position.stock_name} ({position.symbol}), 數量: {position.quantity}, 均價: {position.avg_cost}, 現價: {position.current_price}")
            
            # 驗證計算欄位
            self.assertIsInstance(holdings.total_cost_value, float)
            self.assertIsInstance(holdings.total_market_value, float)
            self.assertGreaterEqual(holdings.total_cost_value, 0)
            self.assertGreaterEqual(holdings.total_market_value, 0)
            
            print(f"✅ 成功取得持股資料")
            print(f"帳戶: {holdings.account.account_id}")
            print(f"持股數量: {len(holdings.positions)}")
            print(f"總成本: {holdings.total_cost_value:,.2f}")
            print(f"總市值: {holdings.total_market_value:,.2f}")
            print(f"總損益: {holdings.total_unrealized_pnl:,.2f}")
            if holdings.total_unrealized_pnl_rate is not None:
                print(f"總損益率: {holdings.total_unrealized_pnl_rate:.2f}%")
            
        except Exception as e:
            self.fail(f"取得玉山持股失敗: {e}")
    
    def test_esun_data_consistency(self):
        """測試玉山資料一致性"""
        try:
            client = EsunClient()
            
            # 連續呼叫兩次，檢查資料一致性
            holdings1 = client.get_holdings()
            holdings2 = client.get_holdings()
            
            # 帳戶資訊應該相同
            self.assertEqual(holdings1.account.account_id, holdings2.account.account_id)
            self.assertEqual(holdings1.account.broker_name, holdings2.account.broker_name)
            
            # 持股數量應該相同（假設短時間內沒有交易）
            self.assertEqual(len(holdings1.positions), len(holdings2.positions))
            
            # 如果有持股，比較持股內容
            if holdings1.positions:
                for pos1, pos2 in zip(holdings1.positions, holdings2.positions):
                    self.assertEqual(pos1.symbol, pos2.symbol)
                    self.assertEqual(pos1.stock_name, pos2.stock_name)
                    self.assertEqual(pos1.quantity, pos2.quantity)
                    self.assertEqual(pos1.avg_cost, pos2.avg_cost)
            
            print(f"✅ 資料一致性測試通過")
            
        except Exception as e:
            self.fail(f"資料一致性測試失敗: {e}")
    
    def test_esun_holdings_position_validation(self):
        """測試玉山持股資料完整性驗證"""
        try:
            client = EsunClient()
            holdings = client.get_holdings()
            
            # 驗證每個持股的資料完整性
            for position in holdings.positions:
                # 基本欄位不能為空
                self.assertTrue(position.symbol, "股票代號不能為空")
              
                
                # 數值欄位應該合理
                self.assertGreaterEqual(position.quantity, 0, f"{position.symbol} 持股數量不能為負數")
                self.assertGreaterEqual(position.avg_cost, 0, f"{position.symbol} 平均成本不能為負數")
                
                # 計算欄位應該正確
                expected_cost_value = position.avg_cost * position.quantity
                self.assertAlmostEqual(position.cost_value, expected_cost_value, places=2, 
                                     msg=f"{position.symbol} 成本金額計算錯誤")
                
                # 如果有現價，市值和損益計算應該正確
                if position.current_price is not None:
                    self.assertGreater(position.current_price, 0, f"{position.symbol} 現價必須大於 0")
                    
                    expected_market_value = position.current_price * position.quantity
                    self.assertAlmostEqual(position.market_value, expected_market_value, places=2,
                                         msg=f"{position.symbol} 市值計算錯誤")
                    
                    expected_unrealized_pnl = expected_market_value - expected_cost_value
                    self.assertAlmostEqual(position.unrealized_pnl, expected_unrealized_pnl, places=2,
                                         msg=f"{position.symbol} 未實現損益計算錯誤")
            
            print(f"✅ 持股資料完整性驗證通過")
            
        except Exception as e:
            self.fail(f"持股資料完整性驗證失敗: {e}")


if __name__ == '__main__':
    # 執行整合測試時顯示詳細輸出
    unittest.main(verbosity=2)
