import unittest
from unittest.mock import patch
from broker.esun.client import EsunClient, EsunSettings


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

    def test_esun_client_get_holdings(self):
        """測試 EsunClient 取得庫存明細"""
        client = EsunClient()
        holdings = client.get_holdings()
        self.assertEqual(holdings, "yes get holdings")

if __name__ == '__main__':
    unittest.main() 