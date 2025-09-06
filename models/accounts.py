from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class Account(BaseModel):
    """帳戶資訊"""
    model_config = ConfigDict(use_enum_values=True)
    
    account_id: str = Field(..., description="帳戶號碼")
    branch_no: Optional[str] = Field(None, description="分公司代號")
    broker_name: str = Field(..., description="券商名稱")
    account_type: Optional[str] = Field(None, description="帳戶類型")
