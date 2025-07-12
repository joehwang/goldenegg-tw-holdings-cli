#! /bin/bash
#!/bin/bash
if [ ! -d ".venv" ]; then
  echo "⚠️  .venv 不存在，是否需要先執行 uv init 或 uv venv .venv？"
  exit 1
fi

source .venv/bin/activate
echo "✅ 已啟動虛擬環境：$(which python)"

# 安裝套件
uv sync