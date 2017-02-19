# coding: utf-8
import tushare as ts
import easytrader as trade
from easytrader import helpers
import pandas as pd
import datetime as dt
import time
from mercury import utils
from mercury import uqer
pd.options.display.max_columns = 100
pd.options.display.max_rows = 300

user = trade.use('yjb')
user.prepare('./guojin.json')

## 查资金
balance = user.balance
## 查持仓
position = user.position

### IPO 自动申购
ipos = helpers.get_today_ipo_data() 
wt = pd.DataFrame(user.entrust)
wt = wt.set_index(wt.entrust_no.values)

if len(ipos)>0:
    for i in range(len(ipos)):
        print(ipos[i])
        ticker = ipos[i]['apply_code']
        limit = user.get_ipo_limit(ticker) ##申购限额
        px = limit['last_price']
        vol = min(limit['enable_amount'],limit['high_amount'])
        print(limit)
        print(ticker,px,vol)
        if not ticker in wt.stock_code.values:
            print(u'新股申购:',ticker,ipos[i]['stock_name'])
            info = user.buy(ticker, price=px, amount=vol)
            print(u"买入委托:", info)
            time.sleep(5)
## 再次查持仓
wt = pd.DataFrame(user.entrust)
wt = wt.set_index(wt.entrust_no.values)
print(u"委托查询:",wt)

###差成交
# deal = pd.DataFrame(user.current_deal)
# deal = deal.set_index(deal.entrust_no.values)
# deal

