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

#优矿token token ='5fa4680adf1c779e93f1d90880b4e2f55a52a7704f2408565ca8c12eebba0469'
#sess = uqer.Client(token='5fa4680adf1c779e93f1d90880b4e2f55a52a7704f2408565ca8c12eebba0469')

yjb = trade.use('yjb')
yjb.prepare('./guojin.json')

## 获取资产情况
balance = yjb.balance
## 获取股票持仓
position = yjb.position
print(balance)

file_name = 'newissue_sh.csv'
newissue = pd.DataFrame()
newissue = newissue.from_csv(file_name, parse_dates=False)
newissue.index = newissue.ticker.apply(lambda x: x[2:8]).values
newissue['open_price'] = newissue.price.apply(lambda x: round(x * 1.20 * 1.20, 2))
print(newissue)
def delayrun():  # 线程运行函数
    for s in newissue.index:
        print(s, newissue.loc[s, 'open_price'], 300)
        info = yjb.buy(s, price=newissue.loc[s, 'open_price'], amount=300)
        print(info)
        pass
# t = Timer(timer_interval,delayrun)
# t.start()
# while (f_time >= 9.15 and f_time <= 10.30) :
icount = 0
flag = True
while icount < 2 and flag == True:
    c_time = dt.datetime.now().strftime('%H.%M%S%f')
    f_time = float(c_time)
    print("now time is : ", f_time)
    if f_time > 9.2503:
        flag = False
    elif f_time > 9.2458:
        delayrun()
        icount += 1
    time.sleep(2)

print('Market is closed...', dt.datetime.now())