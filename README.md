# Golden Egg

## 專案核心理念

**GoldenEgg** 是一個遵循 Model Context Protocol (MCP) 的 Plugin，專注於**持股資訊的標準化儲存與查詢**，採用「分工協作」的現代 AI workflow 設計：

- **LLM Agent**：負責 OCR、圖片解析、資料結構化
- **GoldenEgg Plugin**：負責持股資料的持久化儲存、查詢與統一格式輸出

## 主要功能

### 兩大核心指令
1. **`save_holdings`**：接收 LLM 已解析的持股 JSON，統一格式儲存
2. **`get_holdings`**：查詢持股資料（可來自歷史 OCR 記錄或即時券商 API）

### 支援的資料來源
- **OCR 記憶**：儲存 LLM 解析過的對帳單資料，避免重複辨識
- **券商 API**：即時查詢富邦、永豐、元大、玉山等台灣主要券商

## 系統架構特色

1. **Plugin-aware 設計**：券商模組採 plugin 架構，易於擴充
2. **統一資料格式**：所有來源輸出相同 JSON schema，便於 LLM 工具鏈串接
3. **本地化部署**：在用戶電腦本地運行，確保資料隱私與安全

## 解決的痛點

- **記憶問題**：LLM 每次都要重新解析圖片，無法持久化記憶
- **格式不一**：各券商 API 格式各異，難以整合
- **缺乏標準**：沒有符合 AI Agent 生態的標準化持股 Plugin

## pytest shortcut
```bash
#單測某個function
uv run pytest  -W ignore::DeprecationWarning  -v -s  test/unit/test_shinopac.py -k test_sinopac_client_get_holdings
```

## 注意
- 測試所有integration test `pytest -W ignore::DeprecationWarning  -v -s`
- 測試所有unit test `uv run pytest -W ignore::DeprecationWarning  -v -s test/unit`
- 測試所有unit test 不帶 stdout `uv run pytest -W ignore::DeprecationWarning -s test/unit`
- fubon測試: pytest test/test_fubon_integration.py -v -s 
- 在根目錄的.env可以設定是否測試帳號


## 專案特色

- 支援多個券商 API（玉山、富邦、元大、永豐）
- 使用現代 Python 工具鏈（UV 套件管理器）
- 虛擬環境管理
- 資料處理和分析功能

## 前置需求

- Python 3.13 或更高版本
- UV 套件管理器

## 安裝 UV

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```



## 專案啟動

1. **克隆專案**
```bash
git clone <repository-url>
cd golden-egg
```

2. **使用啟動腳本（推薦）**
```bash
./start.sh
```

這個腳本會：
- 檢查虛擬環境是否存在
- 自動啟動虛擬環境
- 安裝所有依賴套件

3. **手動啟動（替代方案）**
```bash
# 建立虛擬環境


# 啟動虛擬環境
source .venv/bin/activate  # macOS/Linux
# 安裝依賴
uv sync

或是
source ./start.sh
```


## UV 基本用法

### 安裝套件
```bash
# 安裝單一套件
uv add requests

# 安裝開發依賴
uv add --dev pytest

# 安裝指定版本
uv add pandas==2.3.1
```

### 管理依賴
```bash
# 同步依賴（根據 pyproject.toml）
uv sync

# 更新依賴
uv sync --upgrade

# 移除套件
uv remove requests
```

### 執行腳本
```bash
# 在虛擬環境中執行 Python 腳本
uv run python main.py

# 執行測試
uv run pytest
```

## 專案結構

```
golden-egg/
├── main.py              # 主程式入口
├── pyproject.toml       # 專案配置
├── start.sh            # 啟動腳本
├── README.md           # 專案說明
└── broker/            # 券商 API 模組
    ├── esun/          # 玉山證券 API
    ├── fubon_api/     # 富邦證券 API
    ├── masterlink_api/ # 元大證券 API
    └── sinopac/       # 永豐證券 API
```

## 開發指南

### 新增依賴
```bash
uv add <package-name>
```

### 更新依賴
```bash
uv sync --upgrade
```

### 執行專案
```bash
./start.sh
python main.py
```

## 注意事項

- 確保在執行 `start.sh` 前已安裝 UV
- 首次執行時會自動建立虛擬環境
- 所有依賴套件版本都鎖定在 `uv.lock` 中，確保環境一致性

## 授權

[在此填入授權資訊]

## TODO
- unit test 完成了
- intergation test 完成了

在ESUN的docker compose yml看到
```yaml
#這行環境變數的意思是：
##	•	設定 PYTHON_KEYRING_BACKEND 為 keyrings.cryptfile.cryptfile.CryptFileKeyring
#	•	這代表 Python 的 keyring 模組 將會使用 CryptFileKeyring 作為後端。
#	•	CryptFileKeyring 是一個以加密方式儲存憑證（像是 API Token、帳號密碼）的 keyring 實作。
services:
  app:
    build:
      context: .
      dockerfile: DockerFile
    environment:
      - PYTHON_KEYRING_BACKEND=keyrings.cryptfile.cryptfile.CryptFileKeyring
    volumes:
      - .:/app
      - python_keyring:/root/.local/share/python_keyring

volumes:
  python_keyring:
```

## 卷商文件

- 元富(masterlink): https://ml-fugle-api.masterlink.com.tw/FugleSDK/  (沒有測試環境)
- 富邦: https://www.fbs.com.tw/TradeAPI/docs/welcome/#%E6%B8%AC%E8%A9%A6%E7%92%B0%E5%A2%83 (有獨立的測試環境帳號憑證)
- 玉山: https://www.esunsec.com.tw/trading-platforms/api-trading/docs/prerequisites#run_simulation (有測試環境，但是沒有單獨的帳號)
- 永豐證卷: https://sinotrade.github.io/zh/tutor/simulation/ (有測試環境，但要用自已的憑證)