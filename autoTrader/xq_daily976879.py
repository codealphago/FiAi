# -*- coding: utf-8 -*-
import tushare as ts
import easytrader as trade
from easytrader import helpers
import pandas as pd
import numpy as np
import datetime as dt
from mercury import utils
from mercury import uqer
import time
pd.options.display.max_columns = 100
pd.options.display.max_rows = 300
import tushare as tu
from threading import Timer  
import time  

xq = trade.use('xq')
xq.prepare('./xq_daily976879.json')
# 单只股票固定网格动态调仓程序
# 获取基础价格信息
# 单只股票网格调仓策略
ticker = '150212' #新能车B
grid_size = 0.03
grid_range = 4
base_capital = 100000
grid = pd.DataFrame()
base_price = pd.DataFrame()
file_name = 'base_price.csv'
timer_interval=60*5 #时间间隔秒

base_price = base_price.from_csv(file_name,parse_dates = False)
base_px = base_price.price.values[0]
last_pos = base_price.last_pos.values[0]
print("base_price",ticker,base_px,last_pos)
#初始化网格比例
for i in range(grid_range+1):
    grid[grid_range - i] = (round(base_px * ( 1 + i* grid_size),3), 0.5 - (i / (2*grid_range)))
    grid[grid_range + i] = (round(base_px * ( 1 - i* grid_size),3), 0.5 + (i / (2*grid_range)))
grid = grid.T.rename(columns={0:'px',1:'grid'}).sort_index()
# print(grid)


def delayrun(): # 线程运行函数 
    base_price = pd.DataFrame()
    base_price = base_price.from_csv(file_name,parse_dates = False)
    base_px = base_price.price.values[0]
    last_index = base_price.last_pos.values[0]
    print("base_price",ticker,base_px,last_pos)
    #获取实时价格
    today = dt.datetime.now()
    real_px = round(float(ts.get_realtime_quotes(ticker).price.values[0]) ,3)
    print("当前价格",today.strftime('%H:%M'),ticker,real_px)

    adj_index = last_index
    adj_grid = grid.loc[last_index].grid
    if last_index == 0:
        if real_px <= grid.loc[last_index + 1].px:
            adj_grid = grid.loc[last_index + 1].grid
            adj_index = last_index + 1
    elif last_index == len(grid) - 1:
        if real_px >= grid.loc[last_index - 1].px:
            adj_grid = grid.loc[last_index - 1].grid
            adj_index = last_index - 1
    elif last_index > 0 and last_index < len(grid) - 1:
        if real_px <= grid.loc[last_index + 1].px:
            adj_grid = grid.loc[last_index + 1].grid
            adj_index = last_index + 1
        elif real_px >= grid.loc[last_index - 1].px:
            adj_grid = grid.loc[last_index - 1].grid
            adj_index = last_index - 1
        print(adj_index,last_index)
        if adj_index != last_index:
            # 目前雪球的Postion
            pos = pd.DataFrame(xq.position)
            mkv = pd.DataFrame(xq.balance)
            xq_pos = pos.set_index(pos.stock_code.apply(lambda x: x[2:8]).values)
            now_pos = 0.0
            if ticker in xq_pos.index:
                xq_pos['c_pct'] = xq_pos.market_value / mkv.asset_balance.values[0]
                now_pos = xq_pos.loc[ticker, 'c_pct']
                print("now position is ", ticker, now_pos)
            print(now_pos, adj_grid)
            if abs(now_pos - adj_grid) > 0.05 :
                print('按照比例调仓到:',ticker,adj_grid)
                info = xq.adjust_weight(ticker,round(adj_grid*100))
                print(info)
                ## 写入Base price
                base_price['last_pos'] = adj_index
                base_price.to_csv(file_name)

c_time = dt.datetime.now().strftime('%H.%M')
f_time = float(c_time)
while (f_time >= 9.25 and f_time <= 11.30) or  (f_time >= 12.50 and f_time <=15.00):
    print('Market is opening...' ,dt.datetime.now() ) 
    time.sleep(timer_interval)
    delayrun()
    c_time = dt.datetime.now().strftime('%H.%M')
    f_time = float(c_time)

print('Market is closed...' ,dt.datetime.now() ) 