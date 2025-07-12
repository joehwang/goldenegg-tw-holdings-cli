# Golden Egg

一個整合多個券商 API 的 Python 專案，提供統一的交易介面。

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

### 使用 pip 安裝
```bash
pip install uv
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
└── borker/            # 券商 API 模組
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
