from fubon_neo.sdk import FubonSDK, Order
from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction

sdk = FubonSDK()
   
accounts = sdk.login("F124909524", "f108708I", "./F124909524.pfx", "2joixjxi") #若有歸戶，則會回傳多筆帳號資訊
## accounts = sdk.login("您的身分證號", "您的登入密碼", "您的憑證路徑位置")  # 若憑證選用＂預設密碼＂, SDK v1.3.2與較新版本適用
print(accounts)
acc = accounts.data[0]
result=sdk.accounting.inventories(acc)
print(result)
# https://www.fbs.com.tw/TradeAPI/docs/trading/library/python/accountManagement/Inventories/
