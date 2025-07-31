import unittest
from unittest.mock import patch
from broker.masterlink.client import MasterlinkClient, MasterlinkSettings


class TestMasterlinkUnit(unittest.TestCase):
    """簡單的元大證券客戶端單元測試"""

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

    def test_esun_client_get_holdings(self):
        """測試 MasterlinkClient 取得庫存明細"""
        client = MasterlinkClient()
        holdings = client.get_holdings()

        self.assertIn("ok", holdings)
       
if __name__ == '__main__':
    unittest.main() 