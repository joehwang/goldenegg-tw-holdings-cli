# Golden Egg

Golden Egg 是台股券商庫存查詢命令列工具，可查詢並整合富邦、永豐、玉山、台新證券 Nova API 的持股資料。

![image](demo.gif)

## 重要前提

執行本專案前，必須先到各券商完成 API 申請流程。通常包含：

- 申請或啟用證券 API 服務
- 簽署 API 使用風險聲明書或同意書
- 申請並下載交易憑證
- 取得 API Key、API Secret、登入帳號密碼或券商設定檔
- 等待券商完成開通；部分券商簽署後不是立即生效

沒有完成券商端 API 開通時，程式可以安裝，但無法成功登入券商 API。

## 支援券商

| 券商 | broker code | SDK | 登入方式 |
| --- | --- | --- | --- |
| 富邦證券 | `fubon` | `fubon_neo` `2.2.8` | API Key + 憑證 |
| 永豐證券 | `sinopac` | `shioaji` | API Key + API Secret + 憑證 |
| 玉山證券 | `esun` | `esun-trade` | `config.ini` |
| 台新證券 Nova API | `tssco` | `taishin_sdk` `1.0.2` | 帳密 + 憑證 |

各券商申請流程與設定欄位請看 [券商設定文件](docs/brokers.md)。

## 環境需求

- macOS ARM64
- Python 3.13 或更高版本
- uv
- 各券商 API 權限與憑證
- 本地 SDK wheel 檔案放在 `wheels/`

目前 `*.whl` 被 `.gitignore` 忽略。clone 專案後，請依 [券商設定文件](docs/brokers.md) 下載需要的 SDK wheel 到 `wheels/`。

## 安裝 uv

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 安裝依賴

```bash
uv sync
```

可選：安裝成全域命令。

```bash
uv tool install --editable .
```

安裝後可直接使用：

```bash
golden-egg --help
```

## 設定檔模式

本專案透過根目錄 `.env-debug` 決定要讀正式設定還是測試設定。

```bash
EGG_DEBUG=true
```

讀取規則：

| `EGG_DEBUG` | 讀取檔案 |
| --- | --- |
| `true` | `broker/<broker>/.env.test` |
| `false` | `broker/<broker>/.env` |

如果你明明改了 `.env` 但程式沒有吃到，多半是因為 `EGG_DEBUG=true`，程式正在讀 `.env.test`。

## 基本使用

列出支援券商：

```bash
golden-egg brokers
```

查詢全部券商持股：

```bash
golden-egg holdings
```

查詢單一券商：

```bash
golden-egg holdings --broker fubon
```

查詢多個券商：

```bash
golden-egg holdings --broker fubon,esun
```

強制重新呼叫券商 API：

```bash
golden-egg holdings --broker tssco --force-refresh
```

輸出原始 JSON：

```bash
golden-egg holdings --broker fubon --raw
```

尚未安裝全域命令時，也可以用：

```bash
uv run python main.py holdings --broker all
```

## 測試

日常測試：

```bash
uv run pytest -q
```

單元測試：

```bash
uv run pytest -q test/unit
```

單一券商整合測試：

```bash
uv run pytest -W ignore::DeprecationWarning -v -s test/integration/test_fubon_integration.py
uv run pytest -W ignore::DeprecationWarning -v -s test/integration/test_tssco_integration.py
uv run pytest -W ignore::DeprecationWarning -v -s test/integration/test_sinopac_integration.py
uv run pytest -W ignore::DeprecationWarning -v -s test/integration/test_esun_integration.py
```

整合測試會連真實券商 API。若券商端暫時錯誤、rate limit 或尚未開通，測試可能 skip 或失敗。

## 文件

- [券商設定文件](docs/brokers.md)
- [錯誤排查](docs/troubleshooting.md)
- [市場資料 API 規格](docs/market_data_api_spec.md)

## 安全注意事項

- 不要 commit `.env` 或 `.env.test`
- 不要 commit `.p12`、`.pfx`、`config.ini`
- 不要把 API key、API secret、憑證密碼貼到 issue 或 PR
- `wheels/*.whl` 目前不進 git，請在本機自行準備

## 授權

MIT
