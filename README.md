# Golden Egg

Golden Egg 是台股券商庫存查詢命令列工具。目前支援富邦、永豐、元富、玉山等四間證券公司。

![image](demo.gif)

## 前置需求

- 在要連接的卷商申請交易憑證，查看最下方的卷商文件
- Python 3.13 或更高版本
- UV 套件管理器

## 卷商文件

- 元富(masterlink): https://ml-fugle-api.masterlink.com.tw/FugleSDK/  (沒有測試環境)
- 富邦: https://www.fbs.com.tw/TradeAPI/docs/welcome/#%E6%B8%AC%E8%A9%A6%E7%92%B0%E5%A2%83 (有獨立的測試環境帳號憑證)
- 玉山: https://www.esunsec.com.tw/trading-platforms/api-trading/docs/prerequisites#run_simulation (有測試環境，但是沒有單獨的帳號)
- 永豐證卷: https://sinotrade.github.io/zh/tutor/simulation/ (有測試環境，但要用自已的憑證)

## 安裝 UV

### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 安裝依賴

```bash
uv sync
```

## 命令列使用方式

列出支援券商：

```bash
uv run python main.py brokers
```

查詢全部券商持股：

```bash
uv run python main.py holdings
```

查詢單一券商持股：

```bash
uv run python main.py holdings --broker fubon
```

查詢多個券商持股：

```bash
uv run python main.py holdings --broker fubon,esun
```

強制重新呼叫券商 API：

```bash
uv run python main.py holdings --force-refresh
```

輸出原始查詢結果：

```bash
uv run python main.py holdings --raw
```

查看所有命令和參數：

```bash
uv run python main.py --help
uv run python main.py holdings --help
```

如果專案已安裝為可執行指令，也可以使用：

```bash
uv run golden-egg brokers
uv run golden-egg holdings --broker all
```

## 富邦 API Key 登入

富邦新一代 API 自 SDK `2.2.7` 起支援 API Key 登入，SDK `2.2.8` 起支援網頁憑證匯出登入。本專案已改用 `fubon_neo` `2.2.8`。

如果要使用 API Key，請在 `broker/fubon/.env` 加入：

```bash
FUBON_LOGIN_ID=<身分證字號>
FUBON_API_KEY=<富邦 API Key>
FUBON_CERT_FILE=<憑證檔名>
FUBON_CERT_PWD=<憑證密碼，可省略時預設使用身分證字號>
```

富邦目前只支援 API Key 登入，`FUBON_LOGIN_PWD` 不會被使用。

## 驗證卷商是否開通

### 驗證永豐
```bash
uv run pytest -W ignore::DeprecationWarning  -v -s  test/unit/test_shinopac.py 
```
### 驗證富邦
```bash
uv run pytest -W ignore::DeprecationWarning  -v -s  test/unit/test_fubon_unit.py 
```
### 驗證玉山證卷
```bash
uv run pytest -W ignore::DeprecationWarning  -v -s  test/unit/test_esun_unit.py 
```
### 驗證元富證卷
```bash
uv run pytest -W ignore::DeprecationWarning  -v -s  test/unit/test_masterlink_unit.py 
```

## 其他測試
- 測試所有integration test `pytest -W ignore::DeprecationWarning  -v -s`
- 測試所有unit test `uv run pytest -W ignore::DeprecationWarning  -v -s test/unit`
- 測試所有unit test 不帶 stdout `uv run pytest -W ignore::DeprecationWarning -s test/unit`


## 專案結構

```
golden-egg/
├── main.py                    # 主程式入口
├── pyproject.toml             # 專案配置
├── uv.lock                    # UV 依賴鎖定檔案
├── start.sh                   # 啟動腳本
├── README.md                  # 專案說明
├── broker/                    # 券商 API 模組
│   ├── __init__.py
│   ├── base.py                # 券商基礎類別
│   ├── esun/                  # 玉山證券 API
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── certs/             # 玉山憑證檔案
│   │   ├── client.py
│   │   └── reset.py
│   ├── fubon/                 # 富邦證券 API
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── certs/             # 富邦憑證檔案
│   │   ├── client.py
│   │   ├── log/               # 富邦日誌
│   │   ├── ocr_demo.py
│   │   └── ocr.py
│   ├── masterlink/            # 元富證券 API
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── certs/             # 元富憑證檔案
│   │   ├── client.py
│   │   ├── Configs/           # 元富設定檔案
│   │   └── log/               # 元富日誌
│   └── sinopac/               # 永豐證券 API
│       ├── __init__.py
│       ├── certs/             # 永豐憑證檔案
│       └── client.py
├── config/                    # 配置模組
│   ├── __init__.py
│   └── settings.py            # 全域設定
├── docs/                      # 文件目錄
│   └── market_data_api_spec.md
├── log/                       # 全域日誌目錄
├── models/                    # 資料模型
│   ├── __init__.py
│   ├── accounts.py            # 帳戶模型
│   ├── common.py              # 共用模型
│   ├── data/
│   │   └── stock_info.json    # 股票資訊資料
│   ├── holdings.py            # 持股模型
│   └── market_data.py         # 市場資料模型
├── service/                   # 服務層
│   ├── __init__.py
│   ├── cli.py                 # 命令列介面
│   ├── holdings_service.py    # 持股服務
│   └── storage_service.py     # 儲存服務
├── test/                      # 測試目錄
│   ├── conftest.py            # 測試配置
│   ├── integration/           # 整合測試
│   │   ├── __init__.py
│   │   ├── test_esun_integration.py
│   │   ├── test_fubon_integration.py
│   │   ├── test_masterlink_integration.py
│   │   └── test_sinopac_integration.py
│   ├── log/                   # 測試日誌
│   └── unit/                  # 單元測試
│       ├── __init__.py
│       ├── test_esun_unit.py
│       ├── test_fubon_unit.py
│       ├── test_masterlink_unit.py
│       └── test_shinopac.py
└── wheels/                    # WHL 檔案目錄
    └── README.md
```

## 授權
MIT
