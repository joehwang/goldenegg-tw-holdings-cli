# 券商設定文件

Golden Egg 查詢持股前，必須先完成券商端 API 申請與憑證設定。每家券商的流程不同，請先完成官方開通步驟，再設定本專案。

## 設定檔讀取規則

根目錄 `.env-debug` 控制設定模式：

```bash
EGG_DEBUG=true
```

| `EGG_DEBUG` | 讀取檔案 |
| --- | --- |
| `true` | `broker/<broker>/.env.test` |
| `false` | `broker/<broker>/.env` |

## SDK wheel

本專案使用券商提供的本地 wheel。`*.whl` 被 `.gitignore` 忽略，不會進 git。

請將需要的 wheel 放到 `wheels/`，並確認 `pyproject.toml` 的 `[tool.uv.sources]` 指向正確檔名。

目前使用：

| SDK | wheel |
| --- | --- |
| 玉山 | `wheels/esun_trade-2.2.0-cp37-abi3-macosx_11_0_arm64.whl` |
| 富邦 | `wheels/fubon_neo-2.2.8-cp37-abi3-macosx_11_0_arm64.whl` |
| 永豐 | `wheels/shioaji-1.2.6-cp313-cp313-macosx_11_0_arm64.whl` |
| 台新證券 Nova API | `wheels/taishin_sdk-1.0.2-cp37-abi3-macosx_11_0_arm64.whl` |

更新 wheel 後執行：

```bash
uv lock
uv sync
uv tool install --editable . --reinstall
```

## 富邦證券 `fubon`

官方文件：

- https://www.fbs.com.tw/TradeAPI/llms.txt
- 事前準備/API 申請：https://www.fbs.com.tw/TradeAPI/docs/trading/prepare/
- API Key 說明：https://www.fbs.com.tw/TradeAPI/docs/trading/api_key/
- 金鑰申請及管理：https://www.fbs.com.tw/TradeAPI/docs/trading/key/
- 帳務與庫存查詢：https://www.fbs.com.tw/TradeAPI/docs/trading/guide/account_example/

前置作業：

- 依富邦「事前準備」完成 Trade API 申請與啟用
- 取得 API Key
- 申請或匯出有效憑證
- 確認 API Key、身分證字號、憑證檔與憑證密碼相符

憑證放置位置：

```text
broker/fubon/certs/<your-cert>.p12
```

設定檔：

```bash
FUBON_LOGIN_ID=<身分證字號>
FUBON_API_KEY=<富邦 API Key>
FUBON_CERT_FILE=<憑證檔名>
FUBON_CERT_PWD=<憑證密碼>
```

注意事項：

- 富邦目前只支援 API Key 登入。
- `FUBON_LOGIN_PWD` 不會被使用。
- 若 `FUBON_CERT_PWD` 省略，程式會改用 `FUBON_LOGIN_ID` 當憑證密碼。

測試：

```bash
golden-egg holdings --broker fubon --raw --force-refresh
uv run pytest -W ignore::DeprecationWarning -v -s test/integration/test_fubon_integration.py
```

## 台新證券 Nova API `tssco`

官方文件：

- https://ml-fugle-api.tssco.com.tw/FugleSDK/
- https://ml-fugle-api.tssco.com.tw/FugleSDK/llms-full.txt

前置作業：

- 完成線上開戶；若已有台新證券相關帳戶可略過
- 到憑證申請專區申請憑證
- 簽署 API 使用風險暨聲明書
- 等待券商開通生效
- 第一次使用 Nova API 時，依官方文件執行 `register_api_auth` 完成認證

注意事項：

- 簽署完畢後通常不會立即生效，可能需要等待券商作業。
- `register_api_auth` 是首次啟用認證流程，完成後才可使用 SDK 各項功能。

憑證放置位置：

```text
broker/tssco/certs/<your-cert>.p12
```

設定檔：

```bash
TSSCO_LOGIN_ID=<身分證字號>
TSSCO_LOGIN_PWD=<登入密碼>
TSSCO_CERT_FILE=<憑證檔名>
TSSCO_CERT_PWD=<憑證密碼>
```

- 新版 Nova API 的 Python SDK 是 `taishin_sdk`。
- 程式目前仍會讀取舊的 `MASTERLINK_` key 作為相容 fallback；新設定請一律改用 `TSSCO_`。

測試：

```bash
golden-egg holdings --broker tssco --raw --force-refresh
uv run pytest -W ignore::DeprecationWarning -v -s test/integration/test_tssco_integration.py
```

## 永豐證券 `sinopac`

官方文件：

- https://ai.sinotrade.com.tw/python/Main/index.aspx#pag4
- https://sinotrade.github.io/zh/tutor/simulation/

前置作業：

- 完成永豐線上開戶或確認已有電子交易帳戶
- 到簽署中心線上簽署「API電子交易風險預告書暨使用同意書」
- 申請 API Key，以登入 API 服務
- 申請憑證
- 啟用憑證
- 於營業日 8am ~ 8pm 使用 API 模擬環境完成測試
- 等待 API 測試紀錄審核通過後，才會開通 API 下單權限

注意事項：

- 證券與期貨需分別簽署與測試。
- 帳務資料與下單屬於個資相關資料，除了登入驗證外，也需要電子憑證驗證。

憑證放置位置：

```text
broker/sinopac/certs/<your-cert>.pfx
```

設定檔：

```bash
SINOPAC_API_KEY=<API Key>
SINOPAC_API_SECRET=<API Secret>
SINOPAC_CERT_FILE=<憑證檔名>
SINOPAC_CERT_PWD=<憑證密碼>
SINOPAC_PERSON_ID=<身分證字號>
```

測試：

```bash
golden-egg holdings --broker sinopac --raw --force-refresh
uv run pytest -W ignore::DeprecationWarning -v -s test/integration/test_sinopac_integration.py
```

## 玉山證券 `esun`

官方文件：

- https://www.esunsec.com.tw/trading-platforms/api-trading/docs/faq/intro
- https://www.esunsec.com.tw/trading-platforms/api-trading/docs/prerequisites#run_simulation

前置作業：

- 開立或確認已有玉山證券戶
- 申請交易 API 金鑰
- 完成玉山 API 事前準備，以取得開發者權限
- 依官方方式產生或取得設定檔
- 確認設定檔內帳號、憑證與環境正確

注意事項：

- 已有玉山帳戶即可申請交易 API 金鑰。
- 玉山帳戶免費享有基本用戶行情權限。
- 完成事前準備後，可使用開發者權限。
- 玉山證券所有分公司皆開放交易 API 服務。

設定檔放置位置：

```text
broker/esun/certs/config.ini
```

環境設定：

```bash
ESUN_CONFIG_FILE=config.ini
```

測試：

```bash
golden-egg holdings --broker esun --raw --force-refresh
uv run pytest -W ignore::DeprecationWarning -v -s test/integration/test_esun_integration.py
```
