import unittest
from unittest.mock import patch
from broker.fubon.client import FubonClient, FubonSettings


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

    def test_esun_client_get_holdings(self):
        """測試 FubonClient 取得庫存明細"""
        client = FubonClient()
        holdings = client.get_holdings()
        self.assertEqual(holdings, True)
        
if __name__ == '__main__':
    unittest.main() 