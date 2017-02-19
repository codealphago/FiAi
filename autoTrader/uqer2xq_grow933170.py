# -*- coding: utf-8 -*-

import tushare as ts
import easytrader as trade
from easytrader import helpers
import pandas as pd
import datetime as dt
import os,shutil
from mercury import utils
from mercury import uqer
pd.options.display.max_columns = 100
pd.options.display.max_rows = 300

#uquer token ='5fa4680adf1c779e93f1d90880b4e2f55a52a7704f2408565ca8c12eebba0469'
sess = uqer.Client(token='5fa4680adf1c779e93f1d90880b4e2f55a52a7704f2408565ca8c12eebba0469')

user = trade.use('xq')
user.prepare('./xq_grow933170.json')

#下载优矿持仓
today = dt.date.today() 
filename = 'pos'+today.strftime('%Y%m%d')+'.csv'
sess.download_data(filename)
uqer = pd.DataFrame()
uqer = uqer.from_csv(filename)
uqer = uqer.reset_index()
uqer = uqer.set_index(uqer.ticker.apply(lambda x:x[0:6]).values)

##获取雪球当前持仓
pos = pd.DataFrame(user.position)
if len(pos) > 0 :
    mkv = pd.DataFrame(user.balance)
    pos = pos.set_index(pos.stock_code.apply(lambda x:x[2:8]).values)
    pos['c_pct'] = 100.0 * pos.market_value / mkv.asset_balance.values[0] 

## 调整雪球持仓
for s in pos.index:
    if not s in uqer.index:
        print(u'调出: ', pos.loc[s,'stock_name'])
        user.adjust_weight(s,0.0)        
for s in uqer.index:
    pct = round(uqer.loc[s,'pct'] * 100)
    c_pct = 0
    if s in pos.index:
        c_pct = pos.loc[s,'c_pct']
    if abs(c_pct - pct) > 2 : 
        user.adjust_weight(s,pct)

shutil.copyfile(filename,".\\data\\" + filename)    
os.remove(".\\"+filename)