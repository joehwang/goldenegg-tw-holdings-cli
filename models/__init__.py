"""
統一資料模型

本模組定義了所有券商的統一輸出格式，確保：
1. LLM Agent 獲得一致的資料結構
2. MCP Plugin 提供標準化介面
3. 不同券商的資料可以無縫整合

使用方式：
    from models.holdings import Holdings
    from models.common import StockInfoResolver
    from models.market_data import MarketDataProvider
    
    holdings = broker_client.get_holdings()  # 自動轉換為統一格式
    stock_resolver = StockInfoResolver()     # 股票代號名稱轉換
    market_data = MarketDataProvider()       # 市場價格資料
"""
