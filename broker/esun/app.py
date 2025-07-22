from configparser import ConfigParser
from esun_trade.sdk import SDK
from esun_trade.order import OrderObject
from esun_trade.constant import (APCode, Trade, PriceFlag, BSFlag, Action)
# 讀取設定檔
config = ConfigParser()
config.read('./config.simulation.ini')
# 登入
sdk = SDK(config)
sdk.login()



# 庫存明細
inventories = sdk.get_inventories()
print(inventories)
