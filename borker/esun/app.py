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
# 建立委託物件
order = OrderObject(
    buy_sell = Action.Buy,
    price_flag = PriceFlag.LimitDown,
    price = None,
    stock_no = "2884",
    quantity = 1,
)
sdk.place_order(order)
print("Your order has been placed successfully.")

#查委託
orderResults = sdk.get_order_results()
print(orderResults)
# 成交明細 -> 可透過以下兩種 function 進行查詢！
transactions = sdk.get_transactions("0d")
print(transactions)

transactions_by_date = sdk.get_transactions_by_date("2022-10-01", "2023-02-24")
print(transactions_by_date)

# 庫存明細
inventories = sdk.get_inventories()
print(inventories)
