import unittest
from unittest.mock import patch, Mock
from broker.sinopac.client import SinopacClient, SinopacSettings
from models.holdings import Holdings, Position
from models.accounts import Account

class TestSinopacUnit(unittest.TestCase):
    """簡單的永豐金證券客戶端單元測試"""

    def test_sinopac_settings_creation(self):
        """測試 SinopacSettings 基本建立"""
        settings = SinopacSettings()
        self.assertIsInstance(settings, SinopacSettings)

    @patch('broker.sinopac.client.SinopacSettings.get_env_file')
    def test_sinopac_client_creation(self, mock_get_env_file):
        """測試 SinopacClient 基本建立"""
        mock_get_env_file.return_value = "test/.env.test"
        
        client = SinopacClient()
        
        self.assertIsInstance(client, SinopacClient)
        self.assertIsInstance(client.settings, SinopacSettings)

    @patch('broker.sinopac.client.sj.Shioaji')
    @patch('broker.sinopac.client.SinopacSettings.get_env_file')
    def test_sinopac_client_get_holdings(self, mock_get_env_file, mock_shioaji_class):
        """測試 SinopacClient 取得庫存明細"""
        # 設定環境檔案
        mock_get_env_file.return_value = "test/.env.test"
        
        # 設定 mock API
        mock_api = mock_shioaji_class.return_value
        mock_account = Mock()
        mock_account.account_id = "1234567"  # 永豐使用 account_id
        mock_account.branch_id = "001"  # 永豐使用 branch_id
        
        # 模擬 API 回傳
        mock_api.login.return_value = ["success"]
        mock_api.list_accounts.return_value = [mock_account]
        
        # 模擬一個有效持股
        mock_position = Mock()
        mock_position.code = "2330"
        mock_position.quantity = 1000
        mock_position.price = 500.0
        mock_position.last_price = 510.0
        
        mock_api.list_positions.return_value = [mock_position]
        mock_api.activate_ca.return_value = "success"
        
        # 執行測試
        client = SinopacClient()
        holdings = client.get_holdings()
        
        # 驗證結果
        self.assertIsInstance(holdings, Holdings)
        self.assertEqual(holdings.account.broker_name, "永豐證券")
        self.assertEqual(len(holdings.positions), 1)
        self.assertEqual(holdings.positions[0].symbol, "2330")
       
if __name__ == '__main__':
    unittest.main() 