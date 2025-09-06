import unittest
from unittest.mock import patch
from broker.fubon.client import FubonClient, FubonSettings


class MockInventoryOdd:
    """模擬富邦零股資料"""
    def __init__(self, today_qty=0, tradable_qty=0):
        self.today_qty = today_qty
        self.tradable_qty = tradable_qty


class MockInventory:
    """模擬富邦 Inventory 物件"""
    def __init__(self, stock_no, today_qty=0, tradable_qty=0, odd=None):
        self.stock_no = stock_no
        self.today_qty = today_qty
        self.tradable_qty = tradable_qty
        self.odd = odd or MockInventoryOdd()


class TestFubonUnit(unittest.TestCase):
    """簡單的富邦證券客戶端單元測試"""

    def test_fubon_settings_creation(self):
        """測試 FubonSettings 基本建立"""
        settings = FubonSettings()
        self.assertIsInstance(settings, FubonSettings)

    @patch('broker.fubon.client.FubonSettings.get_env_file')
    def test_fubon_client_creation(self, mock_get_env_file):
        """測試 FubonClient 基本建立"""
        mock_get_env_file.return_value = "test/.env.test"
        
        client = FubonClient()
        
        self.assertIsInstance(client, FubonClient)
        self.assertIsInstance(client.settings, FubonSettings)

    # def test_fubon_client_get_holdings(self):
    #     """測試 FubonClient 取得庫存明細 - 需要真實認證，暫時註解"""
    #     client = FubonClient()
    #     holdings = client.get_holdings()
    #     self.assertIsInstance(holdings, Holdings)

    @patch('models.market_data.MarketDataProvider.get_current_price')
    def test_convert_inventory_to_position(self, mock_get_price):
        """測試富邦 Inventory 轉換為 Position 的邏輯"""
        # Mock 市場資料提供者，避免依賴外部 API
        mock_get_price.return_value = None

        # 建立模擬的字典資料（與實際 get_holdings 方法中的格式一致）
        mock_inventory_dict = {
            "stock_no": "2330",
            "today_qty": 2000,
            "tradable_qty": 2000,
            "odd": {
                "today_qty": 100,
                "tradable_qty": 100
            },
            "cost_price": 500.0,
            "unrealized_profit": 1000,
            "unrealized_loss": 0
        }

        client = FubonClient()
        position = client._convert_inventory_to_position(mock_inventory_dict)

        # 驗證轉換結果
        self.assertEqual(position.symbol, "2330")
        self.assertEqual(position.quantity, 2100)  # 2000 + 100
        self.assertEqual(position.available_quantity, 2100)
        self.assertEqual(position.avg_cost, 500.0)
        self.assertIsNone(position.current_price)
    #def test_fubon_client_from_json(self):
    #    """測試 FubonClient 從 JSON 建立"""
    #    client = FubonClient.from_json(json_data)
    #    self.assertIsInstance(client, FubonClient)
    #     self.assertIsInstance(client.settings, FubonSettings)

if __name__ == '__main__':
    unittest.main() 