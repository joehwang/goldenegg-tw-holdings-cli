import unittest
from unittest.mock import patch
from broker.sinopac.client import SinopacClient, SinopacSettings

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

    def test_sinopac_client_get_holdings(self):
        """測試 SinopacClient 取得庫存明細"""
        client = SinopacClient()
        holdings = client.get_holdings()

        # 檢查回傳類型和結構
        self.assertIsInstance(holdings, list, "應該回傳帳戶列表")
        self.assertGreater(len(holdings), 0, "應該至少有一個帳戶")

        # 檢查帳戶物件
        account = holdings[0]
        self.assertTrue(hasattr(account, 'signed'), "帳戶應該有 signed 屬性")
        self.assertIsInstance(account.signed, bool, "signed 應該是布林值")

        # 如果需要檢查簽署狀態
        self.assertTrue(account.signed, "帳戶應該已經簽署")
       
if __name__ == '__main__':
    unittest.main() 