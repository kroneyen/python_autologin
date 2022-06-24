#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

import pandas as pd
import datetime
import time
import requests
from bs4 import BeautifulSoup
import redis
import random
from pymongo import MongoClient

url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.StrictRedis(connection_pool=pool)


def llist(df_len):       
    llist =[] 
    for i in range(df_len) : 
      llist.append(i)
    return llist


def send_line_notify(token,msg):

    requests.post(
    url='https://notify-api.line.me/api/notify',
    headers={"Authorization": "Bearer " + token},
    data={'message': msg}
    )

def get_redis_data(_key,_type,_field_1,_field_2):

    if _type == "lrange" :
       _list = r.lrange(_key,_field_1,_field_2)

    elif _type == "hget" :
       _list = r.hget(_key,_field_1)

    elif _type == "hkeys" :
       _list = r.hkeys(_key)

    return _list


def insert_redis_data(_key,_field_1,_values):

    diic = {  _field_1 :  _values }
   
    r.hmset(_key,diic)
    



# try to instantiate a client instance
c = MongoClient(
        host = 'localhost',
        port = 27017,
        serverSelectionTimeoutMS = 3000, # 3 second timeout
        username = "dba",
        password = "1234",
    )



def insert_mongo_db(_db,_collection,_values):
    db = c[_db] ## database
    collection = db[_collection] ## collection 
    collection.insert_many(_values)


def drop_mongo_db(_db,_collection):
    db = c[_db] ## database
    collection = db[_collection] ## collection 
    ## check collection is exists
    if collection.count() > 0 :
       collection.drop()


def read_mongo_db(_db,_collection,dicct,_columns):
    db = c[_db] ## database
    collection = db[_collection] ## collection 
    #return collection.find({_code:_qq},{"code":1,"name":0,"_id":0,"last_modify":0})
    return collection.find(dicct,_columns)

def read_mongo_db_sort(_db,_collection,dicct,_columns):
    db = c[_db] ## database
    collection = db[_collection] ## collection 
    #return collection.find({_code:_qq},{"code":1,"name":0,"_id":0,"last_modify":0})
    return collection.find(dicct).sort(_columns).liimit(1)



def read_aggregate_mongo(_db,_collection,dicct):
    db = c[_db] ## database
    collection = db[_collection] ## collection 
    return collection.aggregate(dicct)


### mongodb atlas connection
conn_user = get_redis_data('mongodb_user',"hget","user",'NULL')
conn_pwd = get_redis_data('mongodb_user',"hget","pwd",'NULL')

mongourl = 'mongodb+srv://' + conn_user +':' + conn_pwd +'@cluster0.47rpi.gcp.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
conn = MongoClient(mongourl)


def atlas_read_mongo_db(_db,_collection,dicct,_columns):
    db = conn[_db] ## database
    collection = db[_collection] ## collection 
    #return collection.find({_code:_qq},{"code":1,"name":0,"_id":0,"last_modify":0})
    return collection.find(dicct,_columns)





def get_exchange_rate() :

  r = requests.get(url)
  soup = BeautifulSoup(r.text  , "html.parser")
  get_updatetime = soup.find('span',{"class": "time"}).getText()

  df = pd.pandas.read_html(r.text)[0]
  currency_name = []
  currency_code = []
  ## split 幣別 :  '美金, (USD),美金 ,(USD)'
  df['new'] = df.iloc[:,0].str.split(' ',2)
  
  for x in range(len(df['new'])) :
    
    currency_name.append(df['new'][x][0])  ##'美金'
  
    currency_code.append(df['new'][x][1].replace("(","").replace(")",""))  ##'USD'
  
  df['name']= currency_name
  df['code'] = currency_code

  ### get redis data
  #code_list=[]
  #bank_rate_sell_list=[]
  daily_currency_low =[]
  code_list = []
  bank_rate_sell_list=[]  

  
     ## atlas mongo
  _db ='bankrate'
  _collection='target_currency'
  dicct={}
  _columns={"_id":0,"last_modify":0}

  ### atlas mongo 
  try : 
          mongo_mydoc = atlas_read_mongo_db(_db,_collection,dicct,_columns)
  ##local mongo
  except : 
          mongo_mydoc = read_mongo_db(_db,_collection,dicct,_columns)

  ## chk get mongo data   
  if mongo_mydoc.count() >0 :
        #last_day = read_mongo_db_sort(_db,'daily_currency',dicct,{"last_modify":-1}) 

        for idx in mongo_mydoc :
            code_list.append(idx.get('code'))
            bank_rate_sell_list.append(idx.get('bank_rate_sell'))
            #daily_currency_low.qppend(read_mongo_db(_db,'daily_currency',{},{}))
            daily_currency_low.append(get_redis_data('daily_currency_low','hget',idx.get('code'),'NULL')) ## values get from local redis


  else :
        for curr_idx in  get_redis_data('currency','hkeys','NULL','NULL') :
            bank_rate_sell_list.append(get_redis_data('currency','hget',curr_idx,'NULL'))
            daily_currency_low.append(get_redis_data('daily_currency_low','hget',curr_idx,'NULL'))
            code_list.append(curr_idx)
  

  #current_list = get_redis_data('current_list','lrange',0,-1)
  #current_price = get_redis_data('current_price','lrange',0,-1)
  
  df = df.iloc[:,[18,19,1,2,9,10]] ##name ,code 現金 本行買入/賣出  , 即期  買入/賣出
  df.columns= llist(len(df.columns))
  df = df[df[1].isin(code_list)] ##比對 
  df = df.astype({2:'float',3:'float',4:'float',5:'float'})
  df.columns = ['name','code', '現金買','現金賣','即期買', '即期賣']  
  df['buy_rate'] = bank_rate_sell_list ## list_6
  #df['daily_currency_low'] = daily_currency_low  ##list_7
  ###  insert into mongo 
  ori =  datetime.datetime.strptime(get_updatetime, "%Y/%m/%d %H:%M")
  format_str = datetime.datetime.strftime(ori, "%Y%m%d")
  del_format_str =  datetime.datetime.strftime(ori + datetime.timedelta(days = -1), "%Y%m%d") 
  _collections =  'currency_rate_' + format_str 
  d_collections = 'currency_rate_' + del_format_str

  ### delete mongo collection for yesterday 
  
  drop_mongo_db('bankrate',d_collections) 

  #print(df.info())
  ### insert mongo rate data 
  
  _values_list =[]
  for index in range(len(df)) :
    _values = { 'code' : str(df.iloc[index,1]),
                'bank_rate_buy': str(df.iloc[index,2]) , 
                'bank_rate_sell' : str(df.iloc[index,3]),
                'spot_rate_buy' : str(df.iloc[index,4]),
                'spot_rate_sell' : str(df.iloc[index,5]),
                'last_modify':datetime.datetime.now() }

    _values_list.append(_values)
  insert_mongo_db('bankrate',_collections,_values_list)

  ### compare buy price 
  dfs = pd.DataFrame()
  dfs_low = pd.DataFrame()

  for idx in range(len(code_list)) :
    mark_1 = df['現金賣'] < float(bank_rate_sell_list[idx])
    mark_2 = df['code'] == code_list[idx]
    mark_3 = df['現金賣'] < float(daily_currency_low[idx])
    df_mark = df[(mark_1 & mark_2)]
    df_low_mark = df[(mark_2 & mark_3)] 

    dfs = pd.concat([dfs,df_mark],ignore_index=True)
    dfs_low = pd.concat([dfs_low,df_low_mark],ignore_index=True)

  ### merge columns
  dfs['full'] = dfs[['name', 'code']].apply(' '.join, axis=1) ## list_8
  dfs.columns= llist(len(dfs.columns))

  df['full'] = df[['name', 'code']].apply(' '.join, axis=1)
  df.columns= llist(len(df.columns))
  dfs =dfs.iloc[:,[7,2,3,4,5,6]] 
  df =df.iloc[:,[7,2,3,4,5,6]] 
  column_name=['幣別', '現金買','現金賣','即期買', '即期賣','buy_rate']
  dfs.columns = column_name
  df.columns = column_name


  return get_updatetime , dfs  ,df , dfs_low,  _collections


get_updatetime , match_row ,match_df , dfs_low ,data_collections= get_exchange_rate()


def match_row_5 ( get_updatetime ,match_row,extend) : 

          line_key_list =[]
          line_key_list.append( get_redis_data('line_key_hset','hget','Exchange_Rate','NULL')) ## for exchange_rate (Stock_YoY/Stock/rss_google/Exchange_Rate)
          for match_row_index in range(0,len(match_row),5) :
              #msg = get_updatetime + "  " ## for line br
              #msg = get_updatetime  +"\n " + match_row.iloc[match_row_index:match_row_index+5,:].to_string(index = False)  ## for line notify msg 1000  character limit 
              msg = get_updatetime + extend  + match_row.iloc[match_row_index:match_row_index+5,:].to_string(index = False)  ## for line notify msg 1000  character limit 

              ### for multiple line group
              for line_key in  line_key_list : ## 
                  send_line_notify(line_key, msg)
                  time.sleep(random.randrange(1, 3, 1))

   


bank_close_time ='18:05:00'


if not match_row.empty  :

          match_row_5(get_updatetime,match_row,"\n ")

elif not dfs_low.empty :
         for idx in range(len(dfs_low)) :
             ## insert to daily_currency_low  
             insert_redis_data('daily_currency_low',dfs_low.loc[idx]['code'],dfs_low.loc[idx]['現金賣'])


             ## compare currency , daily_currency_low replace 
             #if float(get_redis_data('currency','hget',dfs_low.loc[idx]['code'],'NULL')) > dfs_low.loc[idx]['現金賣']  :
             #        insert_redis_data('currency',dfs_low.loc[idx]['code'],dfs_low.loc[idx]['現金賣'])

         dfs_low =dfs_low.iloc[:,[0,1,3]]
         match_row_5(get_updatetime,dfs_low,"   Daily_low\n")


elif   time.strftime("%H:%M:%S", time.localtime()) > bank_close_time :
       """      
       dicct =  [ 
                {"$match": {"code":"USD" }},
                {"$group": { "_id" : "USD" ,
                             "max" : { "$max" : "$bank_rate_sell"},
                             "min" : { "$min" : "$bank_rate_sell"} ,
                             "now" : { "$last" :"$bank_rate_sell"}}}
                ] 
       """

       dicct =  [ 
                {"$group": { "_id" : "$code" ,
                             "max" : { "$max" : "$bank_rate_sell"},
                             "min" : { "$min" : "$bank_rate_sell"},
                             "now" : { "$last" :"$bank_rate_sell"},
                             "last_modify" : {"$max" :"$last_modify"}}}
                ]

       mongo_doc = read_aggregate_mongo('bankrate',data_collections,dicct)


       ## data format to Dataframe 

       match_row = pd.DataFrame(list(mongo_doc))
       #print(match_row.info())
       
       _values_list = []
       for index in range(len(match_row)) :
            #print(index)
            dd = match_row.iloc[index,4]  
            dd_f =  dd.strftime("%Y%m%d")
            _values = { 'code' : str(match_row.iloc[index,0]) ,
                        'max': str(match_row.iloc[index,1]) ,
                        'min' : str(match_row.iloc[index,2]),
                        'now' : str(match_row.iloc[index,3]),
                        #'date' : match_row.iloc[index,4].strftime("%Y%m%d"),
                        'date' : dd_f,
                        'last_modify':str(match_row.iloc[index,4]) }
                      
            _values_list.append(_values)
       
       ### mongo daily_currency count(*)
       dicct_chk =  [
                { "$match" :{ "date":dd_f }},
                { "$group": { "_id" : "null" ,
                             "count" : { "$sum" : "1" }
                           }
                }
                ]

       mongo_doc_chk = read_aggregate_mongo('bankrate','daily_currency',dicct_chk)
       mongo_doc_count =  pd.DataFrame(list(mongo_doc_chk))
       
       ### mongo is empty of insert    
       if mongo_doc_count.empty  :
       
          insert_mongo_db('bankrate','daily_currency',_values_list)
          match_row_5(get_updatetime,match_row,"\n ")
       

else  :
   print("%s currency is not match buy_price" % get_updatetime)
   print(match_df)
