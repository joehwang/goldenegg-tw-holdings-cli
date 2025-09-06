# models/market_data.py
from typing import Dict, Optional, List
import requests
from datetime import datetime
import json
import urllib3
# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
class MarketDataProvider:
    """市場資料提供者 - 處理即時/歷史股價資料"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def _fetch_twse_data(self, url: str) -> dict:
        """從證交所API獲取資料"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API請求失敗: {response.status_code}")
                return {}
        except Exception as e:
            print(f"獲取市場資料錯誤: {e}")
            return {}
    
    def get_stock_info(self, symbol: str) -> Optional[dict]:
        """取得完整股票資訊
        
        Args:
            symbol: 股票代號 (如 "2330")
            
        Returns:
            包含完整股票資訊的字典或 None
            包含欄位：
            - name: 股票名稱
            - current_price: 最新成交價
            - yesterday_close: 昨收價
            - open_price: 開盤價
            - high_price: 最高價
            - low_price: 最低價
            - volume: 成交量
            - change: 漲跌幅
            - change_percent: 漲跌幅%
        """
        # 台股API - 個股即時行情（支援上市和上櫃）
        # 先嘗試上市 (tse)，如果失敗再嘗試上櫃 (otc)
        for exchange in ['tse', 'otc']:
            url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={exchange}_{symbol}.tw&json=1&delay=0"
            data = self._fetch_twse_data(url)
            
            if data.get('msgArray') and len(data['msgArray']) > 0:
                # 即時報價API回應格式
                raw_info = data['msgArray'][0]
                try:
                    # 解析各種價格資訊
                    def safe_float(value):
                        """安全轉換為浮點數"""
                        if value and value != '-' and value != 'None':
                            return float(value)
                        return None
                    
                    current_price = safe_float(raw_info.get('z'))  # 最新成交價
                    yesterday_close = safe_float(raw_info.get('y'))  # 昨收價
                    
                    # 檢查是否有有效的價格資料，如果沒有就嘗試下一個交易所
                    if not current_price and not yesterday_close:
                        continue  # 靜默跳過無效資料
                    
                    open_price = safe_float(raw_info.get('o'))  # 開盤價
                    high_price = safe_float(raw_info.get('h'))  # 最高價
                    low_price = safe_float(raw_info.get('l'))  # 最低價
                    volume = safe_float(raw_info.get('v'))  # 成交量
                    
                    # 計算漲跌
                    change = None
                    change_percent = None
                    if current_price and yesterday_close and yesterday_close != 0:
                        change = current_price - yesterday_close
                        change_percent = (change / yesterday_close) * 100
                    
                    stock_info = {
                        'symbol': symbol,
                        'name': raw_info.get('n', ''),  # 股票名稱
                        'full_name': raw_info.get('nf', ''),  # 公司全名
                        'current_price': current_price,  # 最新成交價
                        'yesterday_close': yesterday_close,  # 昨收價
                        'open_price': open_price,  # 開盤價
                        'high_price': high_price,  # 最高價
                        'low_price': low_price,  # 最低價
                        'volume': volume,  # 成交量
                        'change': change,  # 漲跌
                        'change_percent': change_percent,  # 漲跌幅%
                        'exchange': exchange,  # 交易所
                        'update_time': raw_info.get('t', ''),  # 更新時間
                        'raw_data': raw_info  # 原始資料
                    }
                    
                    return stock_info
                        
                except (KeyError, ValueError) as e:
                    print(f"解析股票資訊錯誤 ({symbol} @ {exchange}): {e}")
                    continue  # 嘗試下一個交易所
        
        return None

    def get_closing_price(self, symbol: str, date: str = None) -> Optional[float]:
        """取得股票收盤價（保持向後相容）
        
        Args:
            symbol: 股票代號 (如 "2330")
            date: 日期（目前忽略，直接取即時價格）
            
        Returns:
            收盤價或 None
        """
        stock_info = self.get_stock_info(symbol)
        if stock_info:
            return stock_info.get('current_price') or stock_info.get('yesterday_close')
        return None
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """取得股票即時價格"""
        # 可以用即時報價API，這裡先用收盤價代替
        return self.get_closing_price(symbol)
    
    def get_multiple_closing_prices(self, symbols: List[str], date: str = None) -> Dict[str, Optional[float]]:
        """批量取得多檔股票收盤價"""
        result = {}
        for symbol in symbols:
            result[symbol] = self.get_closing_price(symbol, date)
        return result

if __name__ == "__main__":
    provider = MarketDataProvider()
    
    # 測試取得完整股票資訊
    info = provider.get_stock_info("2330")
    if info:
        print(f"=== {info['name']} ({info['symbol']}) ===")
        print(f"最新成交價: {info['current_price']}")
        print(f"昨收價: {info['yesterday_close']}")
        print(f"開盤價: {info['open_price']}")
        print(f"最高價: {info['high_price']}")
        print(f"最低價: {info['low_price']}")
        print(f"成交量: {info['volume']}")
        print(f"漲跌: {info['change']}")
        print(f"漲跌幅: {info['change_percent']:.2f}%" if info['change_percent'] else "N/A")
        print(f"交易所: {info['exchange']}")
    
    # 測試向後相容的收盤價功能
    price = provider.get_closing_price("3081")
    print(f"3081收盤價: {price}")
    
    # 批量測試
    prices = provider.get_multiple_closing_prices(["3081", "2317", "2454"])
    print(f"多檔股票價格: {prices}")
