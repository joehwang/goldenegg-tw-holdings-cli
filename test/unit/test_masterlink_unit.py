import unittest
from unittest.mock import patch, Mock
from broker.masterlink.client import MasterlinkClient, MasterlinkSettings
from models.holdings import Holdings, Position
from models.accounts import Account


class TestMasterlinkUnit(unittest.TestCase):
    """簡單的元富證券客戶端單元測試"""

    def test_masterlink_settings_creation(self):
        """測試 MasterlinkSettings 基本建立"""
        settings = MasterlinkSettings()
        self.assertIsInstance(settings, MasterlinkSettings)

    @patch('broker.masterlink.client.MasterlinkSettings.get_env_file')
    def test_masterlink_client_creation(self, mock_get_env_file):
        """測試 MasterlinkClient 基本建立"""
        mock_get_env_file.return_value = "test/.env.test"
        
        client = MasterlinkClient()
        
        self.assertIsInstance(client, MasterlinkClient)
        self.assertIsInstance(client.settings, MasterlinkSettings)

    @patch('broker.masterlink.client.MasterlinkSettings.create_sdk')
    @patch('broker.masterlink.client.MasterlinkSettings.get_env_file')
    def test_masterlink_client_get_holdings(self, mock_get_env_file, mock_create_sdk):
        """測試 MasterlinkClient 取得庫存明細"""
        # 設定環境檔案
        mock_get_env_file.return_value = "test/.env.test"
        
        # 設定 mock SDK
        mock_sdk = Mock()
        mock_create_sdk.return_value = mock_sdk
        mock_account = Mock()
        mock_account.account = "7654321"  # 元富使用 account 而不是 account_id
        mock_account.branch_name = "測試分行"  # 元富使用 branch_name
        
        # 模擬 API 回傳
        mock_sdk.login.return_value = [mock_account]
        
        # 模擬庫存查詢結果（基於真實元富 API 結構）
        mock_position_summary = Mock()
        mock_position_summary.symbol = "2330"
        mock_position_summary.symbol_name = "台積電"
        mock_position_summary.current_quantity = "2000"
        mock_position_summary.average_price = "600.0"
        mock_position_summary.current_price = "620.0"
        
        mock_inventories_result = Mock()
        mock_inventories_result.position_summaries = [mock_position_summary]
        mock_sdk.accounting.inventories.return_value = mock_inventories_result
        
        # 執行測試
        client = MasterlinkClient()
        holdings = client.get_holdings()
        
        # 驗證結果
        self.assertIsInstance(holdings, Holdings)
        self.assertEqual(holdings.account.broker_name, "元富證券")
        self.assertEqual(len(holdings.positions), 1)
        self.assertEqual(holdings.positions[0].symbol, "2330")
       
if __name__ == '__main__':
    unittest.main() 