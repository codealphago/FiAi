# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 22:32:51 2015

@author: ray
"""

from WindPy import *
import pandas as pd
from sqlalchemy import create_engine
import datetime as dt


engine = create_engine('postgresql+pypostgresql://postgres:postgres@localhost/postgres')

def getIndexPe(code,s_date,e_date):
    w.start()
    df = {}
    #data = w.wsd("000001.SH", "pe_ttm,pb_lf", "2005-11-28", "2015-12-28", "Period=W;Fill=Previous") 
    data = w.wsd(code, "pe_ttm,pb_lf", s_date, e_date, "Period=W;Fill=Previous")     
    if data.ErrorCode == 0:
        df = pd.DataFrame({data.Fields[0] : data.Data[0], data.Fields[1] : data.Data[1]},index=data.Times)
        print(df.tail(12))        
        df.plot(figsize=(14,5),linewidth=2)
        df.hist(normed=1,figsize=(14,5),linewidth=2)
        df['code'] = code
        #df.to_sql('index_factor',engine,schema='stock',if_exists='append')
    return df
    
def saveIndexPe(code,sdate,edate):
    df = getIndexPe(code,sdate,edate)
    df.index = df.index.strftime('%Y-%m-%d')        
    df.to_sql('index_factor',engine,schema='stock',if_exists='replace')

def saveAll(sdate,edate):
    #from 2005-01-01 to 2015-12-29
    hs300 = getIndexPe('000300.SH',sdate,edate)
    hs300.index = hs300.index.strftime('%Y-%m-%d')
    zz500 = getIndexPe('000905.SH',sdate,edate)
    zz500.index = zz500.index.strftime('%Y-%m-%d')
    cyb = getIndexPe('399006.SZ',sdate,edate)
    cyb.index = cyb.index.strftime('%Y-%m-%d')
    sh = getIndexPe('000001.SH',sdate,edate)
    sh.index = sh.index.strftime('%Y-%m-%d')
    sz = getIndexPe('399001.SZ',sdate,edate)
    sz.index = sz.index.strftime('%Y-%m-%d')
    hk = getIndexPe('HSI.HI',sdate,edate)
    hk.index = hk.index.strftime('%Y-%m-%d')
    hkei = getIndexPe('HSCEI.HI',sdate,edate)
    hkei.index = hkei.index.strftime('%Y-%m-%d')
    
    df = hs300.append(zz500)
    df = df.append(cyb)
    df = df.append(sh)
    df = df.append(sz)
    df = df.append(hk)
    df = df.append(hkei)
    df = df.dropna()
    
    df.to_sql('index_factor',engine,schema='stock',if_exists='replace')
    
    
    