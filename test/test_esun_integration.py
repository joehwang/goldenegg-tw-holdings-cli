import pytest
from configparser import ConfigParser
import os
from pathlib import Path

class TestEsunIntegration:
    """整合測試 - 測試真實的 esun API 連線"""
    
    def modify_cert_path(self, config):
        """修改設定檔路徑"""
        cert_relative_path = config.get('Cert', 'Path')
        cert_absolute_path = self.project_root / "borker" / "esun" / cert_relative_path
        config.set('Cert', 'Path', str(cert_absolute_path))
        return config
    
    def setup_method(self):
        """每個測試方法執行前的設定"""
        # 取得專案根目錄
        self.project_root = Path(__file__).parent.parent
        self.config_path = self.project_root / "borker" / "esun" / "config.simulation.ini"
    
    def test_config_file_exists(self):
        """測試設定檔是否存在"""
        assert self.config_path.exists(), f"設定檔不存在: {self.config_path}"
    
    def test_certificate_file_exists(self):
        """測試憑證檔案是否存在"""
        config = ConfigParser()
        config.read(self.config_path)
        
        cert_path = config.get('Cert', 'Path')
        # 處理相對路徑
        if not os.path.isabs(cert_path):
            cert_path = self.project_root / "borker" / "esun" / cert_path
        
        assert os.path.exists(cert_path), f"憑證檔案不存在: {cert_path}"
    
    def test_sdk_creation(self):
        """測試 SDK 物件建立"""
        from esun_trade.sdk import SDK
        
        config = ConfigParser()
        config.read(self.config_path)
        config = self.modify_cert_path(config)
        sdk = SDK(config)
        assert sdk is not None, "SDK 建立失敗"
    
    def test_real_login(self):
        """測試真實登入"""
        from esun_trade.sdk import SDK

        config = ConfigParser()
        config.read(self.config_path)
        config = self.modify_cert_path(config)
        sdk = SDK(config)

        # 實際登入
        login_result = sdk.login()

        # 驗證登入成功
        assert login_result is None, "登入失敗"
        print("✅ 真實登入成功")
    
    def test_real_get_inventories(self):
        """測試真實取得庫存"""
        from esun_trade.sdk import SDK
        
        config = ConfigParser()
        config.read(self.config_path)
        config = self.modify_cert_path(config)

        
        sdk = SDK(config)
        sdk.login()
        
        # 實際取得庫存
        inventories = sdk.get_inventories()
        
        # 驗證回傳的資料
        assert isinstance(inventories, list), "庫存資料應該是列表"
        print(f"✅ 成功取得 {len(inventories)} 筆庫存資料")
        
        # 如果有庫存資料，驗證資料結構
        if inventories:
            first_item = inventories[0]
            assert 'stock_id' in first_item, "庫存資料應包含 stock_id"
            print(f"第一筆庫存: {first_item}")
    
    def test_full_workflow(self):
        """測試完整工作流程"""
        from esun_trade.sdk import SDK
        
        config = ConfigParser()
        config.read(self.config_path)
        config = self.modify_cert_path(config)
        # 1. 建立 SDK
        sdk = SDK(config)
        assert sdk is not None
        
        # 2. 登入
        login_result = sdk.login()
        assert login_result is None
        
        # 3. 取得庫存
        inventories = sdk.get_inventories()
        assert isinstance(inventories, list)
        
        print(f"✅ 完整工作流程測試通過，取得 {len(inventories)} 筆庫存")
