import shioaji as sj
import os
api = sj.Shioaji(simulation=True)
#api = sj.Shioaji()
accounts =  api.login(os.getenv("SHINO_API_KEY"), os.getenv("SHINO_SECRET"))
api.list_accounts()

#api.activate_ca(ca_path="/app/Sinopac.pfx",ca_passwd="F124909524",person_id="F124909524")
print(api.Contracts.Stocks["2408"])
# 商品檔 - 請修改此處
contract = api.Contracts.Stocks.TSE["2408"]

# 證券委託單 - 請修改此處
order = api.Order(
    price=28.1,                                       # 價格
    quantity=1,                                     # 數量
    action=sj.constant.Action.Buy,                  # 買賣別
    price_type=sj.constant.StockPriceType.LMT,      # 委託價格類別
    order_type=sj.constant.OrderType.ROD,           # 委託條件
    account=api.stock_account                       # 下單帳號
)

# 下單
trade = api.place_order(contract, order)
trade