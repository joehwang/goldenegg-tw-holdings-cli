import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from broker.tssco.client import TsscoClient, TsscoSettings
from models.holdings import Holdings


class TestTsscoUnit(unittest.TestCase):
    """簡單的台新證券 Nova API 客戶端單元測試"""

    def _create_env_file(self):
        temp_dir = tempfile.TemporaryDirectory()
        env_path = Path(temp_dir.name) / ".env.test"
        env_path.write_text("", encoding="utf-8")
        self.addCleanup(temp_dir.cleanup)
        return str(env_path)

    def test_tssco_settings_creation(self):
        """測試 TsscoSettings 基本建立"""
        settings = TsscoSettings()
        self.assertIsInstance(settings, TsscoSettings)

    @patch('broker.tssco.client.TsscoSettings.get_env_file')
    def test_tssco_client_creation(self, mock_get_env_file):
        """測試 TsscoClient 基本建立"""
        mock_get_env_file.return_value = self._create_env_file()

        with patch.dict(os.environ, {}, clear=True):
            client = TsscoClient()
        
        self.assertIsInstance(client, TsscoClient)
        self.assertIsInstance(client.settings, TsscoSettings)

    @patch('broker.tssco.client.TsscoSettings.create_sdk')
    @patch('broker.tssco.client.TsscoSettings.get_env_file')
    def test_tssco_client_get_holdings(self, mock_get_env_file, mock_create_sdk):
        """測試 TsscoClient 取得庫存明細"""
        # 設定環境檔案
        mock_get_env_file.return_value = self._create_env_file()
        
        # 設定 mock SDK
        mock_sdk = Mock()
        mock_create_sdk.return_value = mock_sdk
        mock_account = Mock()
        mock_account.account = "7654321"
        mock_account.branch_name = "測試分行"
        
        # 模擬 API 回傳
        mock_sdk.login.return_value = [mock_account]
        
        # 模擬庫存查詢結果（基於真實台新 Nova API 結構）
        mock_position_summary = Mock()
        mock_position_summary.symbol = "2330"
        mock_position_summary.symbol_name = "台積電"
        mock_position_summary.current_quantity = "2000"
        mock_position_summary.average_price = "600.0"
        mock_position_summary.stock_evaluation = "1240000"
        
        mock_inventories_result = Mock()
        mock_inventories_result.position_summaries = [mock_position_summary]
        mock_sdk.accounting.inventories.return_value = mock_inventories_result
        
        # 執行測試
        with patch.dict(os.environ, {}, clear=True):
            client = TsscoClient()
        object.__setattr__(client.settings, "create_sdk", Mock(return_value=mock_sdk))
        holdings = client.get_holdings()
        
        # 驗證結果
        self.assertIsInstance(holdings, Holdings)
        self.assertEqual(holdings.account.broker_name, "台新證券")
        self.assertEqual(len(holdings.positions), 1)
        self.assertEqual(holdings.positions[0].symbol, "2330")

    @patch('broker.tssco.client.TsscoSettings.create_sdk', side_effect=ModuleNotFoundError("No module named 'taishin_sdk'"))
    @patch('broker.tssco.client.TsscoSettings.get_env_file')
    def test_tssco_client_missing_sdk_returns_actionable_error(self, mock_get_env_file, _mock_create_sdk):
        mock_get_env_file.return_value = self._create_env_file()

        with patch.dict(os.environ, {}, clear=True):
            client = TsscoClient()
        object.__setattr__(
            client.settings,
            "create_sdk",
            Mock(side_effect=ModuleNotFoundError("No module named 'taishin_sdk'")),
        )

        with self.assertRaisesRegex(RuntimeError, "taishin-sdk"):
            client.get_holdings()
        
if __name__ == '__main__':
    unittest.main() 
