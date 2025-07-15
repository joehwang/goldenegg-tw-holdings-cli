import sys
from pathlib import Path
import shioaji as sj

# 將專案根目錄加入 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings


# 取得永豐金設定
sinopac_settings = settings.get_shiopac_settings()
print(sinopac_settings)

# 建立 API 實例
api = sj.Shioaji(simulation=sinopac_settings.simulation)
print(sinopac_settings)
# 登入
accounts = api.login(sinopac_settings.api_key, sinopac_settings.api_secret)
print(accounts)

# 查詢帳號列表
account_list = api.list_accounts()
print(account_list)
