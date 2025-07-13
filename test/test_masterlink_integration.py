import pytest
import os
from pathlib import Path

class TestMasterlinkIntegration:
    """整合測試 - 測試 masterlink API 連線"""
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        # 取得專案根目錄
        self.project_root = Path(__file__).parent.parent
        self.app_path = self.project_root / "borker" / "masterlink" / "app.py"
        self.cert_path = self.project_root / "borker" / "masterlink" / "F124909524_20260607_ML.p12"
    
    def test_app_file_exists(self):
        """測試 app.py 檔案是否存在"""
        assert self.app_path.exists(), f"app.py 檔案不存在: {self.app_path}"
    
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
        from masterlink_sdk import MasterlinkSDK
        
        sdk = MasterlinkSDK()
        assert sdk is not None, "SDK 建立失敗"
    
    def test_real_login(self):
        """測試真實登入"""
        from masterlink_sdk import MasterlinkSDK
        
        sdk = MasterlinkSDK()
        
        # 實際登入（使用 app.py 中的參數）
        accounts = sdk.login("F124909524", "f108708I", f"{self.cert_path}", "F124909524")
        
        # 驗證登入結果
        assert accounts is not None, "登入失敗"
        assert len(accounts) > 0, "應至少有一個帳號"
        
        print("✅ 真實登入成功")
        print(f"取得 {len(accounts)} 個帳號")
    
    def test_real_get_inventories(self):
        """測試真實取得庫存"""
        from masterlink_sdk import MasterlinkSDK
        
        sdk = MasterlinkSDK()
        
        # 登入
        accounts = sdk.login("F124909524", "f108708I", f"{self.cert_path}", "F124909524")
        acc = accounts[0]
        
        # 取得庫存
        result = sdk.accounting.inventories(acc)
        
        # 驗證回傳的資料
        assert result is not None, "庫存查詢失敗"
        print(f"✅ 成功取得庫存資料: {result}")
    
    def test_full_workflow(self):
        """測試完整工作流程"""
        from masterlink_sdk import MasterlinkSDK
        
        # 1. 建立 SDK
        sdk = MasterlinkSDK()
        assert sdk is not None
        
        # 2. 登入
        accounts = sdk.login("F124909524", "f108708I", f"{self.cert_path}", "F124909524")
        assert accounts is not None
        assert len(accounts) > 0
        
        # 3. 取得第一個帳號
        acc = accounts[0]
        assert acc is not None
        
        # 4. 取得庫存
        result = sdk.accounting.inventories(acc)
        assert result is not None
        
        print(f"✅ 完整工作流程測試通過")
        print(f"帳號數量: {len(accounts)}")
        print(f"庫存查詢結果: {result}")
    
    def test_app_workflow_simulation(self):
        """模擬 app.py 的完整工作流程"""
        from masterlink_sdk import MasterlinkSDK
        
        # 模擬 app.py 的執行流程
        sdk = MasterlinkSDK()
        
        # 登入（像 app.py 一樣）
        accounts = sdk.login("F124909524", "f108708I", f"{self.cert_path}", "F124909524")
        print(accounts)  # 模擬 app.py 中的 print
        
        # 取得第一個帳號（像 app.py 一樣）
        acc = accounts[0]
        
        # 取得庫存（像 app.py 一樣）
        result = sdk.accounting.inventories(acc)
        print(result)  # 模擬 app.py 中的 print
        
        # 驗證結果
        assert accounts is not None
        assert len(accounts) > 0
        assert result is not None
        
        print("✅ app.py 工作流程模擬測試通過")
    
    