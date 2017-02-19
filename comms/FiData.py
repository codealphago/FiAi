
# coding: utf-8

# ### 数据收集和处理模块: 为tensorflow 等深度学习提供金融数据

import tushare as ts
import datetime as dt
import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn import preprocessing #数据规范化处理
import sklearn as sk

# 公共常量

Src_tu_sina = 1
Src_tu_tx   = 2
Src_wind    = 3 
Src_datayes = 4

Idx_hs300 = '000300'
Idx_sh50  = '000016'
Idx_cyb   = '399006' 
Idx_zz500 = '000905'
Idx_sh01  = '000001'
Idx_sz01  = '399001'
#Idx_hk    = 'HSI'
#Idx_hkgq  = 'HSCEI'

def next_batch(data,i,windows):
    start = np.multiply(i,windows)
    end = start + windows
    total = len(data)
    ret = []
    if start <= total :
        if end <= total : 
            ret = data[start:end]
        else :
            ret = data[start:]
    else :
        ret = []
    return ret

def get_label5(y):
    for i in y.index:
        lab = y.ret[i]
        if lab < -0.03 :
            y.loc[i,'lab'] = 1
        elif lab < -0.005 :
            y.loc[i,'lab'] = 2
        elif lab < 0.005 :
            y.loc[i,'lab'] = 3
        elif lab < 0.03 :
            y.loc[i,'lab'] = 4
        else :
            y.loc[i,'lab'] = 5
    return y.lab.values
def get_label3(y):
    for i in y.index:
        lab = y.ret[i]
        if lab < -0.005 :
            y.loc[i,'lab'] = 1
        elif lab < 0.005 :
            y.loc[i,'lab'] = 2
        else:
            y.loc[i,'lab'] = 3
    return y.lab.values
def get_label2(y):
    for i in y.index:
        if y.ret[i] <= 0 :
            y.loc[i,'lab'] = 1
        else : 
            y.loc[i,'lab'] = 2
    return y.lab.values

# 指数历史数据
def download_data(ticker ,sdate, edate):
    # 历史行情数据
    df = pd.DataFrame()
    days = edate-sdate
    if days.days > 365 : 
        for i in range(int(days.days/365)+1):
            e_date = edate if sdate + (i+1)*dt.timedelta(365) >= edate else  sdate + (i+1)*dt.timedelta(365)
            temp = ts.get_k_data(ticker, start=sdate + i* dt.timedelta(365),end=e_date,index=True)
            df = pd.concat([df,temp],axis=0)
    return df


# 指数历史数据
def get_data(idx ,sdate, edate,norm=False):
    x = pd.DataFrame()
    y = pd.DataFrame()
    df = pd.DataFrame()
    df = download_data(idx,sdate,edate)
    # 历史指标数据
    x = df.dropna()
    x['close'] = x.close.apply(lambda x : float(x) )
    x['open'] = x.open.apply(lambda x : float(x) )
    x['high'] = x.high.apply(lambda x : float(x) )
    x['low'] = x.low.apply(lambda x : float(x) )
    x['volume'] = x.volume.apply(lambda x : float(x) )
    x['c_open'] = x.open / x.close -1.0 
    x['c_high'] = x.high / x.close -1.0 
    x['c_low']  = x.low / x.close -1.0 
    x['c_range'] = (x.high - x.low) / x.close
    x['c_range5'] = x.high.rolling(5).max() - x.low.rolling(5).min() / x.close
    
    x['c_ret5'] = x.close.shift(-5) / x.close - 1.0
    x['c_ret10'] = x.close.shift(-10) / x.close - 1.0
    x['c_ret20'] = x.close.shift(-20) / x.close - 1.0
    
    x['ma5']  = x.close.rolling(5).mean() / x.close -1
    x['ma10'] = x.close.rolling(10).mean() / x.close -1
    x['ma20'] = x.close.rolling(20).mean() /  x.close -1 
    
    x['c_volume'] = x.volume.pct_change()
    x['vma5'] = x.volume.rolling(5).mean() /  x.volume -1
    x['vma10']= x.volume.rolling(10).mean() /  x.volume -1
    x['vma20']= x.volume.rolling(20).mean() / x.volume -1
    x['ret'] = x.close.pct_change()
    x['next_ret'] = x.ret.shift(-1)
    x = x.dropna()
    x = x.reset_index(drop=True)
    y['ret'] = x.next_ret
    x = x.loc[:,['c_range5','c_range','c_ret5','c_ret10','c_ret20','c_open','c_high','c_low','ma5','ma10','ma20','vma5','vma10','vma20','c_volume','ret']]
    if norm == True:
        x = preprocessing.normalize(x, norm='l2')
    else :
        x = x.values
   
    return x , y

def data_roll(x,roll=40) :
    dataimage = []
    for i in range(x.shape[0]-roll):
        df = x[i:i+roll]
        a = df.reshape([1,roll*x.shape[1]])  
        dataimage.append(a)
    dataimage = np.array(dataimage).reshape([x.shape[0]-roll,roll*x.shape[1]])
    return dataimage



