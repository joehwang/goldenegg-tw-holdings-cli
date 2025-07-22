from configparser import ConfigParser
from esun_trade.sdk import SDK
from esun_trade.order import OrderObject
from esun_trade.constant import (APCode, Trade, PriceFlag, BSFlag, Action)

config = ConfigParser()
config.read('./config.simulation.ini') # 請換上您正在使用的 config 檔案
sdk = SDK(config)
sdk.reset_password() # 此函數用來重設密碼
sdk = SDK(config)
sdk.login()