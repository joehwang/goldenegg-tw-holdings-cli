import unittest
from unittest.mock import patch, Mock
from broker.esun.client import EsunClient, EsunSettings
from models.holdings import Holdings, Position
from models.accounts import Account


class TestEsunUnit(unittest.TestCase):
    """簡單的玉山證券客戶端單元測試"""

    def test_esun_settings_creation(self):
        """測試 EsunSettings 基本建立"""
        settings = EsunSettings()
        self.assertIsInstance(settings, EsunSettings)

    @patch('broker.esun.client.EsunSettings.get_env_file')
    def test_esun_client_creation(self, mock_get_env_file):
        """測試 EsunClient 基本建立"""
        mock_get_env_file.return_value = "test/.env.test"
        
        client = EsunClient()
        
        self.assertIsInstance(client, EsunClient)
        self.assertIsInstance(client.settings, EsunSettings)

    @patch('broker.esun.client.EsunSettings.create_sdk')
    @patch('broker.esun.client.EsunSettings.get_env_file')
    def test_esun_client_get_holdings(self, mock_get_env_file, mock_create_sdk):
        """測試 EsunClient 取得庫存明細並轉換為 Holdings 模型"""
        # 設定環境檔案
        mock_get_env_file.return_value = "test/.env.test"
        
        # 設定 mock SDK
        mock_sdk = Mock()
        mock_create_sdk.return_value = mock_sdk
        
        # 模擬玉山庫存 API 回傳格式
        mock_inventories = [
            {
                "cost_sum": "-30148",  # 成本總計
                "make_a_sum": "1054",  # 未實現損益小計
                "price_avg": "29.90",  # 成交均價
                "price_evn": "30.15",  # 損益平衡價
                "stk_na": "玉山金",  # 股票名稱
                "stk_no": "2884",  # 股票代碼
                "stk_dats": [{
                    "fee": "18",  # 手續費
                    "make_a": "1054",  # 未實現損益
                    "pay_n": "-30144",  # 淨收付金額
                    "price": "29.90",  # 成交價格
                    "qty": "1000",  # 庫存股數
                    "t_date": "20220320",  # 成交日期
                    "tax": "0",  # 交易稅
                    "tax_g": "0",  # 證所稅
                    "value_mkt": "31050",  # 市值
                }],
                "value_mkt": "31050",  # 市值
            },
            {
                "cost_sum": "-120000",
                "make_a_sum": "5000",
                "price_avg": "600.00",
                "price_evn": "605.00",
                "stk_na": "台積電",
                "stk_no": "2330",
                "stk_dats": [{
                    "fee": "20",
                    "make_a": "5000",
                    "pay_n": "-120000",
                    "price": "600.00",
                    "qty": "200",
                    "t_date": "20220315",
                    "tax": "0",
                    "tax_g": "0",
                    "value_mkt": "125000",
                }],
                "value_mkt": "125000",
            }
        ]
        
        # 設定 SDK 行為
        mock_sdk.login.return_value = None
        mock_sdk.get_inventories.return_value = mock_inventories
        
        # 執行測試
        client = EsunClient()
        holdings = client.get_holdings()
        
        # 驗證結果
        self.assertIsInstance(holdings, Holdings)
        self.assertEqual(holdings.account.broker_name, "玉山證券")
        self.assertEqual(len(holdings.positions), 2)
        
        # 驗證第一個持股 (玉山金)
        position1 = holdings.positions[0]
        self.assertEqual(position1.symbol, "2884")
        self.assertEqual(position1.stock_name, "玉山金")
        self.assertEqual(position1.quantity, 1000)
        self.assertEqual(position1.avg_cost, 29.90)
        
        # 驗證第二個持股 (台積電)
        position2 = holdings.positions[1]
        self.assertEqual(position2.symbol, "2330")
        self.assertEqual(position2.stock_name, "台積電")
        self.assertEqual(position2.quantity, 200)
        self.assertEqual(position2.avg_cost, 600.00)
        
        # 驗證計算欄位
        self.assertEqual(position1.cost_value, 29900.0)  # 29.90 * 1000
        self.assertEqual(position2.cost_value, 120000.0)  # 600.00 * 200

    @patch('models.market_data.MarketDataProvider.get_current_price')
    def test_convert_inventories_to_positions(self, mock_get_price):
        """測試玉山庫存資料轉換為 Position 的邏輯"""
        # Mock 市場資料提供者，避免依賴外部 API
        mock_get_price.return_value = 31.05

        client = EsunClient()

        # 建立測試資料
        inventories = [
            {
                "cost_sum": "-30148",
                "make_a_sum": "1054",
                "price_avg": "29.90",
                "price_evn": "30.15",
                "stk_na": "玉山金",
                "stk_no": "2884",
                "stk_dats": [{
                    "qty": "1000",
                    "value_mkt": "31050",
                }],
                "value_mkt": "31050",
            }
        ]

        # 執行轉換
        positions = client._convert_inventories_to_positions(inventories)

        # 驗證結果
        self.assertEqual(len(positions), 1)
        position = positions[0]
        self.assertEqual(position.symbol, "2884")
        self.assertEqual(position.stock_name, "玉山金")
        self.assertEqual(position.quantity, 1000)
        self.assertEqual(position.avg_cost, 29.90)
        self.assertEqual(position.current_price, 31.05)  # Mock 的價格

if __name__ == '__main__':
    unittest.main() 