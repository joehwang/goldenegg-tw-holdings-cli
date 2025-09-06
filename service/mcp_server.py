# service/mcp_server.py
"""
Golden Egg FastMCP Server

簡單的 HelloWorld 版本，測試 FastMCP 基本功能
"""

from fastmcp import FastMCP
import asyncio
from service.holdings_service import HoldingsService

# 創建 FastMCP 應用
app = FastMCP("golden-egg")

@app.tool()
async def hello_world(name: str = "World") -> str:
    """簡單的問候工具
    
    Args:
        name: 要問候的名字
        
    Returns:
        問候訊息
    """
    return f"Hello, {name}! 🥚 Welcome to Golden Egg MCP Plugin!"

@app.tool() 
async def get_broker_list() -> str:
    """取得支援的券商清單
    
    Returns:
        券商清單 (JSON 字串)
    """
    import json
    brokers = [
        {"name": "富邦證券", "code": "fubon", "status": "ready"},
        {"name": "永豐證券", "code": "sinopac", "status": "ready"}, 
        {"name": "玉山證券", "code": "esun", "status": "ready"},
        {"name": "元富證券", "code": "masterlink", "status": "ready"}
    ]
    return json.dumps(brokers, ensure_ascii=False, indent=2)

@app.tool()
async def get_holdings(broker: str = "fubon,esun,sinopac,masterlink", force_refresh: bool = False) -> str:
    """取得持股資料
    
    Args:
        broker: 券商代碼，預設為 "fubon,esun,sinopac,masterlink"
        force_refresh: 是否強制重新取得資料（忽略快取），預設為 False
        
    Returns:
        持股資料 (JSON 字串)
    """
    service = HoldingsService()
    holdings_data = await service.get_holdings(broker=broker, force_refresh=force_refresh)
    json_pretty = service.format_holdings_data_json(holdings_data, "股票庫存查詢")
    return service.to_json(json_pretty, ensure_ascii=False, indent=2)


@app.resource("goldenegg://status")
async def get_status():
    """取得服務狀態"""
    return {
        "service": "Golden Egg MCP Plugin",
        "version": "0.1.0",
        "status": "running",
        "supported_tools": ["hello_world", "get_broker_list", "get_holdings"],
        "supported_brokers": ["fubon", "sinopac", "esun", "masterlink"]
    }

def create_server():
    """創建並配置 MCP Server"""
    return app

if __name__ == "__main__":
    print("🥚 Starting Golden Egg MCP Server...")
    print("Available tools:")
    print("  - get_broker_list: 取得券商清單")
    print("Available resources:")
    print("  - goldenegg://status: 服務狀態")
    
    # 啟動 MCP Server (使用 stdio 傳輸)
    app.run(transport="stdio")