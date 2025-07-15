import pytest
import os
from pathlib import Path
import shioaji as sj
from config.settings import settings  # 加入 import
class TestShiopacIntegration:
    """整合測試 - 測試真實的 shioaji (永豐金) API 連線"""

    def setup_method(self):
        """每個測試方法執行前的設定"""
        self.project_root = Path(__file__).parent.parent
        self.settings = settings.get_shiopac_settings()
        

    def test_sdk_import(self):
        """測試 SDK 模組匯入"""
        try:
            import shioaji
            print("✅ shioaji 匯入成功")
        except ImportError as e:
            pytest.fail(f"shioaji 匯入失敗: {e}")

    def test_sdk_creation(self):
        """測試 SDK 物件建立"""
        api = self.settings.create_sdk()
        assert api is not None, "SDK 建立失敗"

    def test_login(self):
        """測試登入 shioaji"""
        api = self.settings.create_sdk()
       
        accounts = api.login(self.settings.api_key, self.settings.api_secret)
        assert accounts is not None, "登入失敗"
        print("✅ 登入成功")
        print(self.settings)
        print(accounts)

    def test_list_accounts(self):
        """測試查詢帳號列表"""
        api = self.settings.create_sdk()
        api.login(self.settings.api_key,  self.settings.api_secret)
        accounts = api.list_accounts()
        assert isinstance(accounts, list), "帳號列表應為 list"
        print(f"✅ 成功取得 {len(accounts)} 個帳號")
        if accounts:
            print(accounts[0])

    def test_full_workflow(self):
        """測試完整工作流程"""
        api = self.settings.create_sdk()
        accounts = api.login(self.settings.api_key,  self.settings.api_secret)
        assert accounts is not None
        assert isinstance(accounts, list) or hasattr(accounts, 'accounts')
        acc_list = api.list_accounts()
        assert isinstance(acc_list, list)
        print(f"✅ 完整工作流程測試通過，帳號數量: {len(acc_list)}")
        if acc_list:
            print(acc_list[0])
