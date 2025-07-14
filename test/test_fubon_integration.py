import pytest
import os
from pathlib import Path
from config.settings import settings  # 加入 import

class TestFubonIntegration:
    """整合測試 - 測試真實的 fubon API 連線"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        # 取得專案根目錄
        self.project_root = Path(__file__).parent.parent
        
        self.cert_path = self.project_root / "borker" / "fubon" 
        self.settings = settings.get_fubon_settings()  # 使用 settings 實例
           
    def test_certificate_file_exists(self):
        """測試憑證檔案是否存在"""
        
        assert self.cert_path.exists(), f"憑證檔案不存在: {self.cert_path}"
    
    def test_sdk_import(self):
        """測試 SDK 模組匯入"""
        try:
            from fubon_neo.sdk import FubonSDK, Order
            from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction
            print("✅ 所有必要模組匯入成功")
        except ImportError as e:
            pytest.fail(f"模組匯入失敗: {e}")
    
    def test_sdk_creation(self):
        """測試 SDK 物件建立"""
        from fubon_neo.sdk import FubonSDK
        
        sdk = self.settings.create_sdk()
        assert sdk is not None, "SDK 建立失敗"

    def test_real_login(self):
        """測試真實登入"""
        from fubon_neo.sdk import FubonSDK
        
        sdk = self.settings.create_sdk()
        
        # 實際登入（使用 app.py 中的參數）
       
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd,
                             f"{self.cert_path}/{self.settings.cert_file}", self.settings.cert_pwd)
        
        # 驗證登入結果
        assert accounts is not None, "登入失敗"
        assert hasattr(accounts, 'data'), "登入結果應包含 data 屬性"
        assert len(accounts.data) > 0, "應至少有一個帳號"
        
        print("✅ 真實登入成功")
        print(f"取得 {len(accounts.data)} 個帳號")
    
    def test_real_get_inventories(self):
        """測試真實取得庫存"""
        from fubon_neo.sdk import FubonSDK
        
        sdk = self.settings.create_sdk()

        
        # 登入
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd,
                             f"{self.cert_path}/{self.settings.cert_file}", self.settings.cert_pwd)
        acc = accounts.data[0]
        
        # 取得庫存
        result = sdk.accounting.inventories(acc)
        
        # 驗證回傳的資料
        assert result is not None, "庫存查詢失敗"
        print(f"✅ 成功取得庫存資料: {result}")
    
    def test_full_workflow(self):
        """測試完整工作流程"""
        from fubon_neo.sdk import FubonSDK
        
        # 1. 建立 SDK
        sdk = self.settings.create_sdk()

        assert sdk is not None
        
        # 2. 登入
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd,
                             f"{self.cert_path}/{self.settings.cert_file}", self.settings.cert_pwd)
        assert accounts is not None
        assert len(accounts.data) > 0
        
        # 3. 取得第一個帳號
        acc = accounts.data[0]
        assert acc is not None
        
        # 4. 取得庫存
        result = sdk.accounting.inventories(acc)
        assert result is not None
        
        print(f"✅ 完整工作流程測試通過")
        print(f"帳號數量: {len(accounts.data)}")
        print(f"庫存查詢結果: {result}")
    
    def test_app_workflow_simulation(self):
        """模擬 app.py 的完整工作流程"""
        from fubon_neo.sdk import FubonSDK
        
        # 模擬 app.py 的執行流程
        sdk = self.settings.create_sdk()

        
        # 登入（像 app.py 一樣）
        accounts = sdk.login(self.settings.login_id, self.settings.login_pwd,
                             f"{self.cert_path}/{self.settings.cert_file}", self.settings.cert_pwd)
        print(accounts)  # 模擬 app.py 中的 print
        print(self.settings.login_id)
        # 取得第一個帳號（像 app.py 一樣）
        acc = accounts.data[0]
        
        # 取得庫存（像 app.py 一樣）
        result = sdk.accounting.inventories(acc)
        print(result)  # 模擬 app.py 中的 print
        
        # 驗證結果
        assert accounts is not None
        assert len(accounts.data) > 0
        assert result is not None
        
        print("✅ app.py 工作流程模擬測試通過")
    
    