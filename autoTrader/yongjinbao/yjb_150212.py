# coding: utf-8
import tushare as ts
import easytrader as trade
import pandas as pd
import datetime as dt
import time
pd.options.display.max_columns = 100
pd.options.display.max_rows = 300

def grid_runer(ticker, trader, mygrid, base_capital):  # 线程运行函数
    base_price = pd.DataFrame()
    base_price = base_price.from_csv(file_name, parse_dates=False)
    last_index = base_price.last_pos.values[0]
    # 获取实时价格
    today = dt.datetime.now()
    real_px = round(float(ts.get_realtime_quotes(ticker).price.values[0]), 3)
    print("当前价格", today.strftime('%H:%M'), ticker, real_px)

    adj_index = last_index
    adj_grid = mygrid.loc[last_index].grid
    if real_px > 0.0:  # 防止停牌或未开始或取得价格有误
        if last_index == 0:
            if real_px <= mygrid.loc[last_index + 1].px:
                adj_grid = mygrid.loc[last_index + 1].grid
                adj_index = last_index + 1
        elif last_index == len(mygrid) - 1:
            if real_px >= mygrid.loc[last_index - 1].px:
                adj_grid = mygrid.loc[last_index - 1].grid
                adj_index = last_index - 1
        elif last_index > 0 and last_index < len(mygrid) - 1:
            if real_px <= mygrid.loc[last_index + 1].px:
                adj_grid = mygrid.loc[last_index + 1].grid
                adj_index = last_index + 1
            elif real_px >= mygrid.loc[last_index - 1].px:
                adj_grid = mygrid.loc[last_index - 1].grid
                adj_index = last_index - 1
    if adj_index != last_index:
        # 目前雪球的Postion
        pos = pd.DataFrame(trader.position)
        mkv = base_capital  # pd.DataFrame(yjb.balance).asset_balance.values[0]
        xq_pos = pos.set_index(pos.stock_code.values)
        xq_pos['c_pct'] = xq_pos.market_value / mkv
        now_pos = 0
        if ticker in xq_pos.index:
            now_pos = xq_pos.loc[ticker, 'c_pct']
        print(adj_index, last_index, now_pos, adj_grid)
        if now_pos - adj_grid > 0.05:
            print('按照比例调仓到:', ticker, adj_grid)
            volume = round((now_pos - adj_grid) * base_capital / real_px / 100) * 100
            if volume > 0:
                info = trader.sell(ticker, price=real_px, amount=volume)  ## 买入委托
                print(info)
                print("sell", ticker, volume, real_px)
                ## 写入Base price
                base_price['last_pos'] = adj_index
                base_price.to_csv(file_name)
        elif now_pos - adj_grid < -0.05:
            print('按照比例调仓到:', ticker, adj_grid)
            volume = round((adj_grid - now_pos) * base_capital / real_px / 100) * 100
            if volume >= 100:
                info = trader.buy(ticker, price=real_px, amount=volume)  ## 买入委托
                print(info)
                print("Buy", ticker, volume, real_px)
                ## 写入Base price
                base_price['last_pos'] = adj_index
                base_price.to_csv(file_name)

######## 网上交易登陆
yjb = trade.use('yjb')
yjb.prepare('./guojin.json')

ticker = '150212'  # 新能车B
grid_size = 0.03
grid_range = 4
capital = 80000
grid = pd.DataFrame()
base_price = pd.DataFrame()
file_name = 'base_price.csv'
timer_interval = 60 * 5  # 时间间隔秒

base_price = base_price.from_csv(file_name, parse_dates=False)
base_px = base_price.price.values[0]
last_pos = base_price.last_pos.values[0]
print("base_price", ticker, base_px, last_pos)
# 初始化网格比例
for i in range(grid_range + 1):
    grid[grid_range - i] = (round(base_px * (1 + i * grid_size), 3), 0.5 - (i / (2 * grid_range)))
    grid[grid_range + i] = (round(base_px * (1 - i * grid_size), 3), 0.5 + (i / (2 * grid_range)))
grid = grid.T.rename(columns={0: 'px', 1: 'grid'}).sort_index()
print(grid)

c_time = dt.datetime.now().strftime('%H.%M')
f_time = float(c_time)
while (f_time >= 9.30 and f_time <= 11.30) or (f_time >= 13.00 and f_time <= 15.00):
    print('Market is opening...', dt.datetime.now())
    time.sleep(timer_interval)
    grid_runer(ticker, yjb,grid,capital)
    c_time = dt.datetime.now().strftime("%H.%M")
    f_time = float(c_time)

print('Market is closed...', dt.datetime.now())