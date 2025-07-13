# pip install masterlinksdk-3.11-cp37-abi3-win_amd64.whl

from masterlink_sdk import MasterlinkSDK, Order, TimeInForce, OrderType, PriceType, MarketType, BSAction
# 載入設定檔與登入
sdk = MasterlinkSDK()
accounts = sdk.login("F124909524", "f108708I",
                     "./F124909524_20260607_ML.p12", "F124909524")   # 若是使用技術文件申請，則憑證密碼為預設
# accounts = sdk.login("您的身分證字號", "您的登入密碼", "您的憑證位置", "您的憑證密碼") # 若使用憑證 e 管家，則需輸入自設憑證密碼

acc = accounts[0]

# res=sdk.register_api_auth(acc)  # 未開通過元富 API 之用戶，第一次登入時，需加入此行程式認證，認證完畢後，即可移除此行
# print(res)
print(sdk.accounting.inventories(acc))
