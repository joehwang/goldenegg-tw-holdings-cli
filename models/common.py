from enum import Enum
from typing import Optional
from pathlib import Path
import json
import requests
import pandas as pd
import urllib3
from io import StringIO

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MarketType(Enum):
    """市場類型統一定義"""
    # 台灣股市
    TSE = "TSE"          # 台灣證券交易所（上市）
    OTC = "OTC"          # 櫃買中心（上櫃）
    EMERGING = "EMERGING" # 興櫃市場
    
    # 國際市場
    US = "US"            # 美股
    HK = "HK"            #  港股
    
    # 其他
    UNKNOWN = "UNKNOWN"   # 未知市場
    

class StockInfoResolver:
    """股票號碼轉名稱"""
    def __init__(self):
        self.stock_info_file = Path(__file__).parent/ "data"/ "stock_info.json"
        self.stock_info = self._load_stock_info()

    def _load_stock_info(self) -> dict:
        if  not self.stock_info_file.exists():
            print(f"Stock info file not found: {self.stock_info_file}")
            self.fetch_from_twse()
        with open(self.stock_info_file, 'r') as file:
            return json.load(file)

    def _fetch_web_content(self, url: str) -> dict:
        """通用的網頁內容獲取函數，以網址為參數回傳字典"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        try:
            print(f"Fetching from: {url}")
            res = requests.get(url, headers=headers, timeout=30, verify=False)
            print(f"Status code: {res.status_code}")
            
            if res.status_code == 200:
                return {"success": True, "content": res.text, "url": url}
            else:
                return {"error": f"HTTP {res.status_code}", "url": url}
                
        except Exception as e:
            print(f"Error fetching from {url}: {e}")
            return {"error": str(e), "url": url}

    def _parse_twse_html(self, html_content: str, source_name: str = "") -> dict:
        """解析證交所的 HTML 內容，回傳股票資訊字典"""
        try:
            df = pd.read_html(StringIO(html_content))[0]
            # 設定column名稱
            df.columns = df.iloc[0]
            # 刪除第一行
            df = df.iloc[1:]
            # 先移除row，再移除column，超過三個NaN則移除
            df = df.dropna(thresh=3, axis=0).dropna(thresh=3, axis=1)
            df = df.set_index('有價證券代號及名稱')
            # 處理股票代號和名稱，格式如 "1236　宏亞"
            processed_data = {}
            
            for index, row in df.iterrows():
                if pd.notna(index):
                    index_str = str(index).strip()
                   
                    parts = None
                    for separator in ['　']: 
                        if separator in index_str:
                            parts = index_str.split(separator, 1)
                            break
                    
                    if parts and len(parts) == 2:
                        stock_code = parts[0].strip()
                        stock_name = parts[1].strip()
                        
                        # 只保留代碼長度 <= 5 的項目
                        if len(stock_code) <= 5:
                            processed_data[stock_code] = {
                                'name': stock_name,
                                'source': source_name,  # 標記資料來源
                                **row.to_dict()  # 包含其他欄位資訊
                            }
            
            print(f"解析 {len(processed_data)} 筆股票資訊 ({source_name})")
            return processed_data
            
        except Exception as e:
            print(f"Error parsing HTML content ({source_name}): {e}")
            return {}

    def fetch_from_twse(self) -> dict:
        """從多個來源獲取股票資訊並合併"""
        # 定義資料來源
        sources = {
            "上市": "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2",  # 上市
            "上櫃": "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4",  # 上櫃
        }
        
        all_stock_data = {}
        
        for source_name, url in sources.items():
            print(f"\n開始獲取{source_name}股票資料...")
            
            # 獲取網頁內容
            result = self._fetch_web_content(url)
            
            if not result.get("success"):
                print(f"無法獲取{source_name}資料: {result.get('error')}")
                continue
            
            # 解析HTML內容
            stock_data = self._parse_twse_html(result["content"], source_name)
            
            # 合併資料
            for stock_code, stock_info in stock_data.items():
                if stock_code in all_stock_data:
                    # 如果已存在，合併資訊（保留原有資料，添加來源資訊）
                    existing_source = all_stock_data[stock_code].get('source', '')
                    if source_name not in existing_source:
                        all_stock_data[stock_code]['source'] = f"{existing_source},{source_name}".strip(',')
                else:
                    # 新增股票資料
                    all_stock_data[stock_code] = stock_info
        
        # 儲存合併後的資料
        if all_stock_data:
            self._save_stock_data(all_stock_data)
        
        return all_stock_data

    def _save_stock_data(self, stock_data: dict):
        """儲存股票資料到JSON檔案"""
        # 確保data目錄存在
        self.stock_info_file.parent.mkdir(exist_ok=True)
        
        # 保存到JSON文件
        with open(self.stock_info_file, 'w', encoding='utf-8') as file:
            json.dump(stock_data, file, ensure_ascii=False, indent=2)
        
        print(f"保存 {len(stock_data)} 筆股票資訊到 {self.stock_info_file}")




    def get_stock_info(self, stock_no: str) -> dict:
        return self.stock_info.get(stock_no, {})

    def get_stock_name(self, stock_no: str) -> str:
        stock_info = self.stock_info.get(stock_no, {})
        return stock_info.get('name', '未知股票')  
    
if __name__ == "__main__":
    resolver = StockInfoResolver()
    print(resolver.get_stock_info("2330"))