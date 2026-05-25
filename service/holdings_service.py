# service/holdings_service.py
"""
持股資料服務

負責：
1. 統一的 get_holdings 介面
2. 整合多個券商的資料
3. 資料格式標準化
4. 自動快取管理 (使用 cachetools)
"""

from typing import List, Dict, Optional, Literal, Any
from datetime import datetime
import asyncio
import json
import pprint
from concurrent.futures import ThreadPoolExecutor
from cachetools import TTLCache

from broker.fubon.client import FubonClient
from broker.esun.client import EsunClient
from broker.sinopac.client import SinopacClient
from broker.masterlink.client import MasterlinkClient
from models.holdings import Holdings, Position
from models.accounts import Account


class HoldingsService:
    """持股資料服務"""
    
    @staticmethod
    def datetime_serializer(obj):
        """自定義 datetime 序列化器
        
        Args:
            obj: 需要序列化的對象
            
        Returns:
            序列化後的值
            
        Raises:
            TypeError: 如果對象不可序列化
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    @staticmethod
    def to_json(data: Dict, ensure_ascii: bool = False, indent: int = 2) -> str:
        """將數據轉換為 JSON 字串
        
        Args:
            data: 要序列化的數據
            ensure_ascii: 是否確保 ASCII 編碼
            indent: 縮進空格數
            
        Returns:
            JSON 字串
        """
        return json.dumps(
            data, 
            ensure_ascii=ensure_ascii, 
            indent=indent, 
            default=HoldingsService.datetime_serializer
        )
    
    def __init__(self, cache_ttl_seconds: int = 300, cache_maxsize: int = 50):
        """
        初始化持股服務
        
        Args:
            cache_ttl_seconds: 快取存活時間（秒），預設 5 分鐘
            cache_maxsize: 快取最大項目數，預設 50 個
        """
        self.brokers = {
            'fubon': FubonClient,
            'esun': EsunClient,
            'sinopac': SinopacClient,
            'masterlink': MasterlinkClient
        }
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 使用 cachetools 的 TTL 快取
        self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl_seconds)
        
        print(f"🚀 HoldingsService 初始化完成")
        print(f"   快取設定: {cache_maxsize} 個項目，TTL {cache_ttl_seconds} 秒")
    
    async def get_holdings(
        self,
        broker: Optional[str] = None,
        update_prices: bool = True,
        force_refresh: bool = False
    ) -> Dict[str, any]:
        """
        統一的持股資料查詢介面
        
        Args:
            broker: 券商代碼，可以是：
                   - 單一券商: "fubon"
                   - 多券商: "fubon,esun"  
                   - 全部券商: "all" 或 None
            update_prices: 是否更新最新價格
            force_refresh: 是否強制重新取得資料（忽略快取）
            
        Returns:
            標準化的持股資料字典
        """
        try:
            broker_codes = self._parse_broker_codes(broker)
            cache_key = f"holdings_{'-'.join(sorted(broker_codes))}_prices_{update_prices}"
            
            # 檢查快取（除非強制刷新）
            if not force_refresh and cache_key in self.cache:
                cached_result = self.cache[cache_key].copy()
                cached_result["from_cache"] = True
                cached_result["cache_hit_time"] = datetime.now().isoformat()
                print(f"📋 使用快取資料 (券商: {broker or 'all'})")
                return cached_result
            
            # 快取未命中，呼叫 API
            print(f"🔄 呼叫券商 API (券商: {broker or 'all'})")
            result = await self._fetch_from_api(broker_codes, update_prices)
            
            # 儲存到快取
            if result["success"]:
                # 移除 cache 相關欄位再存入快取
                cache_data = result.copy()
                cache_data.pop("from_cache", None)
                cache_data.pop("cache_hit_time", None)
                
                self.cache[cache_key] = cache_data
                print(f"💾 資料已儲存到快取 (key: {cache_key})")
            
            result["from_cache"] = False
            return result
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "from_cache": False,
                "timestamp": datetime.now().isoformat()
            }
    

    
    async def _fetch_from_api(self, broker_codes: List[str], update_prices: bool) -> Dict[str, any]:
        """從券商 API 取得持股資料"""
        if len(broker_codes) == 1:
            # 單一券商
            broker_code = broker_codes[0]
            holdings = await self._get_single_broker_holdings(broker_code)
            if not holdings:
                return {
                    "success": False,
                    "source": "api",
                    "broker": broker_code,
                    "data": None,
                    "error": f"取得 {broker_code} 持股資料失敗",
                    "timestamp": datetime.now().isoformat()
                }
            if holdings and update_prices:
                holdings = holdings.update_current_prices()
            
            return {
                "success": True,
                "source": "api",
                "broker": broker_code,
                "data": holdings.model_dump() if holdings else None,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # 多券商整合
            holdings_dict = await self._get_multiple_broker_holdings(broker_codes)
            if not holdings_dict:
                return {
                    "success": False,
                    "source": "api",
                    "broker": "merged",
                    "broker_list": broker_codes,
                    "data": None,
                    "individual_data": {},
                    "error": "所有券商持股資料取得失敗",
                    "timestamp": datetime.now().isoformat()
                }
            merged_holdings = self._merge_holdings(holdings_dict)
            
            if merged_holdings and update_prices:
                merged_holdings = merged_holdings.update_current_prices()
            
            return {
                "success": True,
                "source": "api", 
                "broker": "merged",
                "broker_list": list(holdings_dict.keys()),
                "data": merged_holdings.model_dump() if merged_holdings else None,
                "individual_data": {k: v.model_dump() for k, v in holdings_dict.items()},
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_broker_codes(self, broker: Optional[str]) -> List[str]:
        """解析券商代碼"""
        if not broker or broker == "all":
            return list(self.brokers.keys())
        
        if "," in broker:
            codes = [code.strip() for code in broker.split(",")]
            return [code for code in codes if code in self.brokers]
        
        if broker in self.brokers:
            return [broker]
        
        raise ValueError(f"不支援的券商代碼: {broker}")
    
    async def _get_single_broker_holdings(self, broker_code: str) -> Optional[Holdings]:
        """取得單一券商持股資料"""
        try:
            client_class = self.brokers[broker_code]
            loop = asyncio.get_event_loop()
            
            holdings = await loop.run_in_executor(
                self.executor,
                self._sync_get_holdings,
                client_class
            )
            return holdings
        except Exception as e:
            print(f"❌ 取得 {broker_code} 持股資料失敗: {e}")
            return None
    
    async def _get_multiple_broker_holdings(self, broker_codes: List[str]) -> Dict[str, Holdings]:
        """並行取得多個券商持股資料"""
        tasks = []
        for broker_code in broker_codes:
            task = asyncio.create_task(
                self._get_single_broker_holdings(broker_code)
            )
            tasks.append((broker_code, task))
        
        results = {}
        for broker_code, task in tasks:
            try:
                holdings = await task
                if holdings:
                    results[broker_code] = holdings
            except Exception as e:
                print(f"❌ 取得 {broker_code} 持股資料失敗: {e}")
        
        return results
    
    def _sync_get_holdings(self, client_class) -> Holdings:
        """同步執行券商 API 呼叫"""
        client = client_class()
        return client.get_holdings()
    
    def _merge_holdings(self, holdings_dict: Dict[str, Holdings]) -> Optional[Holdings]:
        """合併多個券商的持股資料"""
        if not holdings_dict:
            return None
        
        # 合併所有持股
        merged_positions: Dict[str, Position] = {}
        all_accounts = []
        
        for broker_code, holdings in holdings_dict.items():
            all_accounts.append(holdings.account)
            
            for position in holdings.positions:
                symbol = position.symbol
                
                if symbol in merged_positions:
                    # 股票已存在，合併數量和重新計算平均成本
                    existing = merged_positions[symbol]
                    
                    # 計算加權平均成本
                    total_cost = (existing.avg_cost * existing.quantity + 
                                position.avg_cost * position.quantity)
                    total_quantity = existing.quantity + position.quantity
                    new_avg_cost = total_cost / total_quantity if total_quantity > 0 else 0
                    
                    # 更新持股資料
                    merged_positions[symbol] = Position(
                        symbol=symbol,
                        market=position.market or existing.market,
                        quantity=total_quantity,
                        available_quantity=(existing.available_quantity or 0) + 
                                         (position.available_quantity or 0),
                        avg_cost=new_avg_cost,
                        current_price=position.current_price or existing.current_price,
                        broker_code=f"{existing.broker_code},{position.broker_code}" if existing.broker_code and position.broker_code else (existing.broker_code or position.broker_code),
                        broker_name=f"{existing.broker_name},{position.broker_name}" if existing.broker_name and position.broker_name else (existing.broker_name or position.broker_name)
                    )
                else:
                    # 新股票，直接加入
                    merged_positions[symbol] = position
        
        # 建立合併帳戶資訊
        broker_names = [acc.broker_name for acc in all_accounts]
        merged_account = Account(
            account_id="MERGED",
            broker_name=f"整合帳戶({', '.join(broker_names)})",
            account_type="合併"
        )
        
        # 建立合併後的 Holdings
        return Holdings(
            account=merged_account,
            positions=list(merged_positions.values()),
            data_source="api",
            update_time=datetime.now()
        )
    
    def get_cache_info(self) -> Dict[str, any]:
        """取得快取資訊"""
        return {
            "current_size": self.cache.currsize,
            "max_size": self.cache.maxsize,
            "ttl_seconds": self.cache.ttl,
            "cache_keys": list(self.cache.keys())
        }
    
    def clear_cache(self) -> Dict[str, any]:
        """清空快取"""
        cleared_count = len(self.cache)
        self.cache.clear()
        print(f"🗑️ 已清空 {cleared_count} 個快取項目")
        return {
            "cleared_items": cleared_count,
            "message": f"已清空 {cleared_count} 個快取項目"
        }
    
    def get_supported_brokers(self) -> List[Dict[str, str]]:
        """取得支援的券商清單"""
        return [
            {"code": "fubon", "name": "富邦證券", "status": "ready"},
            {"code": "esun", "name": "玉山證券", "status": "ready"},
            {"code": "sinopac", "name": "永豐證券", "status": "ready"},
            {"code": "masterlink", "name": "元富證券", "status": "ready"}
        ]

    def format_holdings_data_json(self, result: dict, title: str) -> Dict[str, Any]:
        """格式化持股資料為 JSON 結構
        
        Args:
            result: 持股查詢結果
            title: 報告標題
            
        Returns:
            結構化的 JSON 格式持股資料
        """
        formatted_result = {
            "title": title,
            "basic_info": {
                "query_status": "成功" if result.get('success') else '失敗',
                "data_source": "快取" if result.get('from_cache') else 'API',
                "timestamp": result.get('timestamp', '無')
            },
            "account_info": None,
            "summary": None,
            "positions": [],
            "raw_data": result
        }

        if 'data' in result and result['data']:
            data = result['data']

            # 帳戶資訊
            if 'account' in data and data['account']:
                account = data['account']
                formatted_result["account_info"] = {
                    "account_id": account.get('account_id', '無'),
                    "broker_name": account.get('broker_name', '無'),
                    "branch_no": account.get('branch_no', '無'),
                    "account_type": account.get('account_type', '無')
                }

            # 總計資訊
            formatted_result["summary"] = {
                "total_quantity": data.get('total_quantity', 0),
                "total_cost_value": data.get('total_cost_value', 0),
                "total_market_value": data.get('total_market_value', 0),
                "total_unrealized_pnl": data.get('total_unrealized_pnl', 0),
                "total_unrealized_pnl_rate": data.get('total_unrealized_pnl_rate', 0)
            }

            # 個股明細
            if 'positions' in data and data['positions']:
                for pos in data['positions']:
                    position_data = {
                        "broker_name": pos.get('broker_name', ''),
                        "symbol": pos.get('symbol', ''),
                        "stock_name": pos.get('stock_name', ''),
                        "quantity": pos.get('quantity', 0),
                        "available_quantity": pos.get('available_quantity', 0),
                        "avg_cost": pos.get('avg_cost', 0),
                        "current_price": pos.get('current_price', 0),
                        "market_value": pos.get('market_value', 0),
                        "unrealized_pnl": pos.get('unrealized_pnl', 0),
                        "unrealized_pnl_rate": pos.get('unrealized_pnl_rate', 0),
                        "cost_value": pos.get('cost_value', 0),
                        "broker_code": pos.get('broker_code', ''),
                        "market": pos.get('market', None)
                    }
                    formatted_result["positions"].append(position_data)

        return formatted_result

# 使用範例
def print_holdings_data(result: dict, title: str):
    """格式化輸出持股資料"""
    print(f"\n{'='*60}")
    print(f"📊 {title}")
    print(f"{'='*60}")
    
    # 基本資訊
    print(f"🔍 查詢狀態: {'成功' if result.get('success') else '失敗'}")
    print(f"📋 資料來源: {'快取' if result.get('from_cache') else 'API'}")
    print(f"🕐 時間戳記: {result.get('timestamp', '無')}")
   
    
    if 'data' in result:
        data = result['data']
        
        # 帳戶資訊
        if 'account' in data:
            account = data['account']
            print(f"\n📋 帳戶資訊:")
            print(f"   帳戶ID: {account.get('account_id', '無')}")
            print(f"   券商名稱: {account.get('broker_name', '無')}")
            print(f"   分公司: {account.get('branch_no', '無')}")
        
        # 總計資訊
        print(f"\n💰 總計資訊:")
        print(f"   總持股數量: {data.get('total_quantity', 0):,}")
        print(f"   總成本價值: ${data.get('total_cost_value', 0):,.2f}")
        print(f"   總市值: ${data.get('total_market_value', 0):,.2f}")
        print(f"   總未實現損益: ${data.get('total_unrealized_pnl', 0):,.2f}")
        print(f"   總報酬率: {data.get('total_unrealized_pnl_rate', 0):.2f}%")
        
        # 個股明細
        if 'positions' in data and data['positions']:
            print(f"\n📈 個股明細:")
            print(f"{'券商':<8} {'股票代號':<8} {'股票名稱':<12} {'數量':<8} {'成本':<8} {'現價':<8} {'市值':<12} {'損益':<12} {'報酬率':<8}")
            print("-" * 80)
            
            for pos in data['positions']:
    
                broker_name = pos.get('broker_name', '')
                symbol = pos.get('symbol', '')
                name = pos.get('stock_name', '')[:10]  # 限制名稱長度
                quantity = pos.get('quantity', 0)
                cost = pos.get('avg_cost', 0)
                price = pos.get('current_price', 0)
                market_value = pos.get('market_value', 0)
                pnl = pos.get('unrealized_pnl', 0)
                pnl_rate = pos.get('unrealized_pnl_rate', 0)
                
                print(f"{broker_name:<8} {symbol:<8} {name:<12} {quantity:<8,} ${cost:<7.2f} ${price:<7.2f} ${market_value:<11,.0f} ${pnl:<11,.0f} {pnl_rate:<7.2f}%")
    
    print(f"{'='*60}\n")


if __name__ == "__main__":
    """使用範例 - 展示更好的設計模式"""
    service = HoldingsService(cache_ttl_seconds=300)  # 5 分鐘快取
    
    
    # 步驟 1: 取得資料
    print("🔄 步驟 1: 取得持股資料")
    holdings_data = service.get_holdings(broker="fubon,esun,sinopac,masterlink")
    print(f"✅ 資料取得成功: {holdings_data.get('success', False)}")

    
    r=service.format_holdings_data_json(holdings_data, "第一次查詢結果 (API)")
    print(r)







    
