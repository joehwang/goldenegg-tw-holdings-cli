# 錯誤排查

本文件整理 Golden Egg 常見安裝、設定與券商 API 錯誤。

## 設定檔沒有生效

先確認根目錄 `.env-debug`：

```bash
EGG_DEBUG=true
```

讀取規則：

| `EGG_DEBUG` | 讀取檔案 |
| --- | --- |
| `true` | `broker/<broker>/.env.test` |
| `false` | `broker/<broker>/.env` |

如果你改了 `.env`，但 `EGG_DEBUG=true`，程式會讀 `.env.test`。

## `No module named taishin_sdk`

代表目前環境沒有安裝台新證券 Nova API SDK。

確認 wheel 存在：

```bash
ls wheels/taishin_sdk-1.0.2-cp37-abi3-macosx_11_0_arm64.whl
```

重新同步：

```bash
uv sync
uv tool install --editable . --reinstall
```

## `No module named fubon_neo`

代表目前環境沒有安裝富邦 SDK。

確認 wheel 存在：

```bash
ls wheels/fubon_neo-2.2.8-cp37-abi3-macosx_11_0_arm64.whl
```

重新同步：

```bash
uv sync
uv tool install --editable . --reinstall
```

## 富邦：`Cert Expired`

富邦憑證過期。請到富邦重新申請或匯出有效憑證，放到：

```text
broker/fubon/certs/
```

並更新：

```bash
FUBON_CERT_FILE=<新憑證檔名>
```

## 富邦：`certificate password wrong`

常見原因：

- `FUBON_CERT_PWD` 錯誤
- `FUBON_LOGIN_ID` 空白或不是憑證所屬身分證字號
- `FUBON_CERT_FILE` 指到錯誤憑證

先檢查：

```bash
FUBON_LOGIN_ID=<身分證字號>
FUBON_API_KEY=<富邦 API Key>
FUBON_CERT_FILE=<憑證檔名>
FUBON_CERT_PWD=<憑證密碼>
```

## 富邦：`缺少 FUBON_API_KEY 設定`

富邦目前只支援 API Key 登入。請先向富邦申請 Trade API 與 API Key，然後設定：

```bash
FUBON_API_KEY=<富邦 API Key>
```

## 玉山：`AGR0003: Exceed Transaction Rate Limit`

玉山 API rate limit。等待 1 分鐘後再重試。

## 永豐：登入成功但帳務或下單失敗

永豐帳務資料與下單需要電子憑證驗證，也需要完成 API 申請流程。

請確認：

- 已簽署「API電子交易風險預告書暨使用同意書」
- 已申請 API Key
- 已申請並啟用憑證
- 已於模擬環境完成 API 測試
- API 測試紀錄已審核通過
- 證券與期貨權限是否分別完成申請與測試

## 台新證券 Nova API：`EOF while parsing a value`

常見原因：

- 使用舊版 Nova SDK
- 券商 API 回空 response
- API 權限尚未生效
- 憑證或登入資料錯誤

目前專案應使用：

```text
taishin_sdk 1.0.2
```

確認：

```bash
uv run python -c "import importlib.metadata as m; print(m.version('taishin-sdk'))"
```

## 台新證券 Nova API 第一次登入失敗

新版 Nova API 文件提到，未開通過台新 API 的用戶第一次登入時，可能需要執行官方的 `register_api_auth`。

請先依官方文件完成：

- 線上開戶或帳戶確認
- 申請憑證
- 簽署 API 使用風險暨聲明書
- `register_api_auth`

## `uv sync` 找不到 wheel

因為 `wheels/*.whl` 不進 git，clone 專案後需要自行下載券商 SDK wheel。

確認 `pyproject.toml` 的 `[tool.uv.sources]` 和 `wheels/` 內檔名一致。

## 全域 `golden-egg` 還是用舊 SDK

如果你更新了 `pyproject.toml` 或 wheel，但全域命令仍報舊錯誤，請重裝 tool：

```bash
uv tool install --editable . --reinstall
```

## integration test 失敗或 skip

integration tests 會打真實券商 API。以下情況可能導致 skip 或失敗：

- 尚未申請券商 API
- API 權限尚未生效
- 憑證過期
- 憑證密碼錯誤
- 券商 API 暫時異常
- rate limit
- 非交易時段或券商系統維護

單元測試可用來檢查程式邏輯：

```bash
uv run pytest -q test/unit
```
