# models/holdings.py
from pydantic import BaseModel, Field, computed_field, ConfigDict
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from .accounts import Account
from .common import MarketType, StockInfoResolver
from .market_data import MarketDataProvider


class Position(BaseModel):
    """個股持股明細"""
    #個設定控制 Enum 怎麼被序列化，設定才能輸入json字串
    model_config = ConfigDict(use_enum_values=True) 
    
    symbol: str = Field(..., description="股票代號", json_schema_extra={"example": "2330"})
    
    market: Optional[MarketType] = Field(None, description="市場別")
    
    # 持股數據
    quantity: int = Field(..., description="持有股數", ge=0)
    available_quantity: Optional[int] = Field(None, description="可賣股數")
    avg_cost: float = Field(..., description="平均成本", ge=0)
    current_price: Optional[float] = Field(None, description="現價")
    # 券商資訊（支援多券商）
    broker_code: Optional[str] = Field(None, description="券商代碼")
    broker_name: Optional[str] = Field(None, description="券商名稱")
    broker_details: Optional[List[Dict[str, Any]]] = Field(None, description="詳細券商資訊列表")

    # 自動轉換股票名稱
    @computed_field
    @property
    def stock_name(self) -> str:
        """股票名稱"""
        return StockInfoResolver().get_stock_name(self.symbol)
    
    # 自動計算欄位
    @computed_field
    @property
    def cost_value(self) -> float:
        """成本金額"""
        return self.avg_cost * self.quantity
    
    @computed_field  
    @property
    def market_value(self) -> Optional[float]:
        """市值"""
        if self.current_price is None:
            return None
        return self.current_price * self.quantity
    
    @computed_field
    @property 
    def unrealized_pnl(self) -> Optional[float]:
        """未實現損益"""
        if self.market_value is None:
            return None
        return self.market_value - self.cost_value
    
    @computed_field
    @property
    def unrealized_pnl_rate(self) -> Optional[float]:
        """未實現損益率%"""
        if self.unrealized_pnl is None or self.cost_value == 0:
            return None
        return (self.unrealized_pnl / self.cost_value) * 100

class Holdings(BaseModel):
    """完整持股資訊"""
    model_config = ConfigDict(use_enum_values=True, json_encoders={datetime: lambda v: v.isoformat()})
    
    account: Account = Field(..., description="帳戶資訊")
    positions: List[Position] = Field(default_factory=list, description="持股明細")
    
    # 元資料
    update_time: datetime = Field(default_factory=datetime.now, description="更新時間")
    data_source: Literal["api", "cache", "manual"] = Field("api", description="資料來源")
    
    #add total_quantity
    @computed_field
    @property
    def total_quantity(self) -> int:
        """總持股數量"""
        return sum(p.quantity for p in self.positions)
    
    @computed_field
    @property
    def total_market_value(self) -> float:
        """總市值"""
        return float(sum(p.market_value or 0 for p in self.positions))
    
    @computed_field
    @property 
    def total_cost_value(self) -> float:
        """總成本"""
        return float(sum(p.cost_value for p in self.positions))
    
    @computed_field
    @property
    def total_unrealized_pnl(self) -> float:
        """總未實現損益"""
        return float(sum(p.unrealized_pnl or 0 for p in self.positions))
    
    @computed_field
    @property
    def total_unrealized_pnl_rate(self) -> Optional[float]:
        """總未實現損益率%"""
        if self.total_cost_value == 0:
            return None
        return (self.total_unrealized_pnl / self.total_cost_value) * 100
    
    def update_current_prices(self, date: str = None) -> 'Holdings':
        """更新所有持股的最新價格
        
        Args:
            date: 指定日期 YYYYMMDD，預設為今天
            
        Returns:
            更新後的 Holdings 物件
        """
        market_data = MarketDataProvider()
        symbols = [position.symbol for position in self.positions]
        
        # 批量取得價格
        prices = market_data.get_multiple_closing_prices(symbols, date)
        
        # 更新每個持股的現價
        updated_positions = []
        for position in self.positions:
            position_data = position.model_dump()
            if prices.get(position.symbol) is not None:
                position_data['current_price'] = prices[position.symbol]
            updated_positions.append(Position(**position_data))
        
        # 建立新的 Holdings 物件
        updated_data = self.model_dump()
        updated_data['positions'] = updated_positions
        updated_data['update_time'] = datetime.now()
        
        return Holdings(**updated_data)