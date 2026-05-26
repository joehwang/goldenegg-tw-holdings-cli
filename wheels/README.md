# 券商 SDK Wheel 檔案

此目錄包含各券商的 Python SDK wheel 檔案。

## 檔案清單

- `esun_trade-2.0.0-cp37-abi3-macosx_11_0_arm64.whl` - 玉山證券 SDK
- `fubon_neo-2.2.8-cp37-abi3-macosx_11_0_arm64.whl` - 富邦證券 SDK  
- `taishin_sdk-1.0.2-cp37-abi3-macosx_11_0_arm64.whl` - 台新證券 Nova API SDK

## 注意事項

- 這些檔案目前只支援 macOS ARM64 平台
- 如需其他平台支援，請聯繫相關券商取得對應的 wheel 檔案
- 安裝時會自動透過 pyproject.toml 的配置載入

## 更新方式

當券商提供新版本時：
1. 下載新的 whl 檔案到此目錄
2. 更新 pyproject.toml 中的路徑
3. 執行 `uv sync` 重新安裝依賴
