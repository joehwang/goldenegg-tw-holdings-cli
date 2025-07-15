import pytest
import os
from pathlib import Path
from config.settings import settings  # 加入 import

class TestMasterlinkIntegration:
    """整合測試 - 測試真實的 masterlink API 連線"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.project_root = Path(__file__).parent.parent
        self.settings = settings.get_masterlink_settings()
        self.cert_path = self.project_root / "borker" / "masterlink" / self.settings.cert_file
    
    def test_certificate_file_exists(self):
        """測試憑證檔案是否存在"""
        assert self.cert_path.exists(), f"憑證檔案不存在: {self.cert_path}"
    
    def test_sdk_import(self):
        """測試 SDK 模組匯入"""
        try:
            from masterlink_sdk import MasterlinkSDK, Order, TimeInForce, OrderType, PriceType, MarketType, BSAction
            print("✅ 所有必要模組匯入成功")
        except ImportError as e:
            pytest.fail(f"模組匯入失敗: {e}")
    
    def test_sdk_creation(self):
        """測試 SDK 物件建立"""
        sdk = self.settings.create_sdk()
        assert sdk is not None, "SDK 建立失敗"

    def test_real_login(self):
        """測試真實登入"""
        sdk = self.settings.create_sdk()
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd, str(self.cert_path), self.settings.cert_pwd)
        assert accounts is not None, "登入失敗"
        assert len(accounts) > 0, "應至少有一個帳號"
        print("✅ 真實登入成功")
        print(f"取得 {len(accounts)} 個帳號")

    def test_real_get_inventories(self):
        """測試真實取得庫存"""
        sdk = self.settings.create_sdk()
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd, str(self.cert_path), self.settings.cert_pwd)
        acc = accounts[0]
        result = sdk.accounting.inventories(acc)
        assert result is not None, "庫存查詢失敗"
        print(f"✅ 成功取得庫存資料: {result}")

    def test_full_workflow(self):
        """測試完整工作流程"""
        sdk = self.settings.create_sdk()
        assert sdk is not None
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd, str(self.cert_path), self.settings.cert_pwd)
        assert accounts is not None
        assert len(accounts) > 0
        acc = accounts[0]
        assert acc is not None
        result = sdk.accounting.inventories(acc)
        assert result is not None
        print(f"✅ 完整工作流程測試通過")
        print(f"帳號數量: {len(accounts)}")
        print(f"庫存查詢結果: {result}")

    def test_app_workflow_simulation(self):
        """模擬 app.py 的完整工作流程"""
        sdk = self.settings.create_sdk()
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd, str(self.cert_path), self.settings.cert_pwd)
        print(accounts)
        acc = accounts[0]
        result = sdk.accounting.inventories(acc)
        print(result)
        assert accounts is not None
        assert len(accounts) > 0
        assert result is not None
        print("✅ app.py 工作流程模擬測試通過")
    
    