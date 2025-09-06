# main.py
"""
Golden Egg MCP Server 啟動入口

用途：
1. 啟動 FastMCP Server
2. 註冊 Tools, Resources, Prompts
3. 處理命令列參數
4. 配置日誌和錯誤處理
"""

from service.mcp_server import create_server

if __name__ == "__main__":
    print("🚀 Golden Egg MCP Server Starting...")
    
    # 創建並啟動 MCP Server
    server = create_server()
    server.run(transport="stdio")