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
import re
import send_mail
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.font_manager import fontManager
import del_png




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
"""
def send_line_notify(token,msg):

    requests.post(
    url='https://notify-api.line.me/api/notify',
    headers={"Authorization": "Bearer " + token},
    data={'message': msg ,
          stickerPackageId": "446",
          "stickerId": "1988"}
    )
"""




def get_redis_data(_key,_type,_field_1,_field_2):

    if _type == "lrange" :
       _list = r.lrange(_key,_field_1,_field_2)

    elif _type == "hget" :
       _list = r.hget(_key,_field_1)

    elif _type == "hgetall" :
       _list = r.hgetall(_key)

    elif _type == "hkeys" :
       _list = r.hkeys(_key)

    return _list


def insert_redis_data(_key,_field_1,_values):

    diic = {  _field_1 :  _values }
   
    r.hmset(_key,diic)
    

def hmset_insert_redis_data(_key,dicct):

    r.hmset(_key,dicct)


def delete_redis_data(_key):
    r.delete(_key)



# try to instantiate a client instance
c = MongoClient(
        host = 'localhost',
        port = 27017,
        serverSelectionTimeoutMS = 3000, # 3 second timeout
        username = "dba",
        password = "1234",
    )



def insert_many_mongo_db(_db,_collection,_values):
    db = c[_db] ## database
    collection = db[_collection] ## collection 
    collection.insert_many(_values)


def delete_many_mongo_db(_db,_collection,dicct):
    db = c[_db] ## database
    collection = db[_collection] ## collection 
    collection.delete_many(dicct)



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
    return collection.find(dicct).sort(_columns).limit(1)




def read_aggregate_mongo(_db,_collection,dicct):
    db = c[_db] ## database
    collection = db[_collection] ## collection 
    return collection.aggregate(dicct)


def getCollectionNames_mongo (_db):
    db = c[_db] ## database
    return db.list_collection_names()


def name_regex(values) : 
    collection_list=[]
    for idx in values : 
      if  re.match( '^currency_rate',idx ) :
        collection_list.append(idx)
    return collection_list

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

  mongo_mydoc_df = pd.DataFrame(list(mongo_mydoc))
  ## chk get mongo data   
  if not mongo_mydoc_df.empty :
        code_list = list(mongo_mydoc_df['code'])
        bank_rate_sell_list= list(mongo_mydoc_df['bank_rate_sell']) 
        for idx in code_list : 
            daily_currency_low.append(get_redis_data('daily_currency_low','hget',idx,'NULL')) ## values get from local redi      

        ##insert local mongo
        local_mongo = read_mongo_db(_db,_collection,dicct,_columns)
        local_mongo_df = pd.DataFrame(list(local_mongo))
        chk_mongo = mongo_mydoc_df.equals(local_mongo_df)
        ##insert local mongo & redis sync
        if chk_mongo == False:
           if not  mongo_mydoc_df.empty :
              drop_mongo_db(_db,_collection)
              records= mongo_mydoc_df.copy()
              records['last_modify']= datetime.datetime.now()
              records = records.to_dict(orient='records')
              insert_many_mongo_db(_db,_collection,records)
        
              ##insert local redis
              delete_redis_data('target_currency')
              records = { k: v for k, v in zip(code_list, bank_rate_sell_list) }
              hmset_insert_redis_data(_collection,records)
  
  else : ## get redis data 
        for curr_idx in  get_redis_data('target_currency','hkeys','NULL','NULL') :
            bank_rate_sell_list.append(get_redis_data('target_currency','hget',curr_idx,'NULL'))
            daily_currency_low.append(get_redis_data('daily_currency_low','hget',curr_idx,'NULL'))
            code_list.append(curr_idx)
  

  df = df.iloc[:,[18,19,1,2,9,10]] ##name ,code 現金 本行買入/賣出  , 即期  買入/賣出
  df.columns= llist(len(df.columns))
  df = df[df[1].isin(code_list)] ##比對 
  df = df.astype({2:'float',3:'float',4:'float',5:'float'})
  df.columns = ['name','code', '現金買','現金賣','即期買', '即期賣'] 
  ### merge target bank_rate_sell 
  df =  pd.merge(df, mongo_mydoc_df  , on = ['code'],how='left')
  df.rename(columns={'bank_rate_sell' : 'target'}, inplace=True)
  ###  insert into mongo 
  ori =  datetime.datetime.strptime(get_updatetime, "%Y/%m/%d %H:%M")
  format_str = datetime.datetime.strftime(ori, "%Y%m%d")
  _collections =  'currency_rate_' + format_str 
  ### delete mongo collection for yesterday 
  mydoc = getCollectionNames_mongo('bankrate') 
  coll_doc =  name_regex(mydoc)
  for idx in  coll_doc: 
      ### 保留最後一個
      if idx != _collections : 
         drop_mongo_db('bankrate',idx)
 
  #print(df)
  ### Before insert of get monog data last row
  dicct = [  {"$group" : {"_id" : "$code" ,"last_now" : {"$last" : "$bank_rate_sell"}     }}]
  
  last_price = read_aggregate_mongo('bankrate',_collections,dicct)
  last_price_df = pd.DataFrame(list(last_price))
  #print('dfffff:',df)
  ### insert mongo rate data 
  records = df.copy()
  records['last_modify']  = datetime.datetime.now()
  records.rename(columns={'現金買':'bank_rate_buy','現金賣':'bank_rate_sell','即期買':'spot_rate_buy','即期賣':'spot_rate_sell'}, inplace=True)
  records = records.iloc[:,[1,2,3,4,5,7]]
  records = records.to_dict(orient='records')
  #print('recordscurrency_rate_20240624:',records)
  insert_many_mongo_db('bankrate',_collections,records)

  ### compare buy price 
  dfs = pd.DataFrame()
  df_com = pd.DataFrame()
  dfs_low = pd.DataFrame()
  for idx in range(len(code_list)) :
    mark_1 = df['現金賣'] < float(bank_rate_sell_list[idx])
    mark_2 = df['code'] == code_list[idx]
    mark_3 = df['現金賣'] < float(daily_currency_low[idx])
    df_mark = df[(mark_1 & mark_2)]
    df_low_mark = df[(mark_2 & mark_3)] 

    ### Low then Target Price
    dfs = pd.concat([dfs,df_mark],ignore_index=True)
    ### Low then Daily Price 
    dfs_low = pd.concat([dfs_low,df_low_mark],ignore_index=True)

  ### set compare dataframe 
  df_com = df.copy()

  ### merge columns
  dfs['full'] = dfs[['name', 'code']].apply(' '.join, axis=1) ## list_8
  dfs.columns= llist(len(dfs.columns))

  df['full'] = df[['name', 'code']].apply(' '.join, axis=1)
  df.columns= llist(len(df.columns))
   
  #print('dfs:',dfs)
  #print('df:',df)  

  #dfs.columns= llist(len(dfs.columns))
  #df.columns= llist(len(df.columns)) 

  dfs =dfs.iloc[:,[7,2,3,4,5,6]] 
  df =df.iloc[:,[7,2,3,4,5,6]] 
  #column_name=['幣別', '現金買','現金賣','即期買', '即期賣','buy_rate']
  column_name=['幣別', '現金買','現金賣','即期買', '即期賣','target']
  dfs.columns = column_name
  df.columns = column_name

  return get_updatetime , dfs  ,df , dfs_low, df_com ,  _collections ,last_price_df


get_updatetime , match_row ,match_df , dfs_low ,df_com ,data_collections , last_price_df = get_exchange_rate()


#print('match_row:',match_row)
#print('match_df:',match_df)

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

   


def avg_daily_currency(_collection): 

    _db = 'bankrate'
    
    dictt_avg = [ {"$group" : {"_id" : "$code" ,  "min_price" :   {"$min" : "$bank_rate_sell" } , 
                                                  "max_price" :   {"$max" : "$bank_rate_sell" } ,
                                                  "now_price" :   {"$last" : "$bank_rate_sell"  } ,  
                                                  "avg_price" :   {"$avg" : { "$toDouble" :"$bank_rate_sell" }  } 
                              }   
                  }, 
                  { "$project" : { "_id" : 0, "code" : "$_id" , "min"	: "$min_price",  "max"	: "$max_price" , "now"	: "$now_price", "avg"	: {"$round": ["$avg_price" , 4] }  }  
                  } 	            
                ]

    avg_price = read_aggregate_mongo(_db,_collection,dictt_avg)

    avg_price_df = pd.DataFrame(list(avg_price))    

    return avg_price_df.iloc[:,[0,4]]



def Plot_Exchange_Rate(date,code_lists) :

   dfs = pd.DataFrame()

   colors = ['tab:blue', 'tab:orange', 'tab:red', 'tab:green', 'tab:gray']
   
   code_num = 0 
    
   for code_idx in code_lists :

      altas_mydoc = read_mongo_db('bankrate','daily_currency',{'code': code_idx ,'date': {'$gte' : date}},{'_id':0 ,'code':1,'now':1 ,'date':1})


      df = pd.DataFrame(list(altas_mydoc))

      #df.rename(columns={'now': idx}, inplace=True)

      rest_df = pd.DataFrame(data = df['now'].values,columns=[code_idx] , index=df['date'])
      #match_row =pd.merge( pd.merge(match_row,df_auth_stock,on = ['code'],how='left'),df_cal_day_conti,on = ['code'],how='left')
      
      for idx in range(0,len(rest_df.columns),5):

        idx_records = rest_df.iloc[ : , idx:idx+5 ]
        ax = idx_records.plot(y = idx_records.columns ,color=colors[code_num] )
        ## 顯示數據
        for line, name in zip(ax.lines, idx_records.columns):
           y = line.get_ydata()[-1]
           #ax.annotate(name, xy=(1,y), xytext=(4,0), color=line.get_color(),
           ax.annotate(name, xy=(1,y), xytext=(4,0), color=colors[code_num],                       
                xycoords = ax.get_yaxis_transform(), textcoords="offset points",
                size=10, va="center")

      #plt.savefig('./images/image_'+ str(idx) +'_'+ str(idx+4) +'.png' )
      plt.savefig('./images/image_'+ code_idx +'_'+ str(idx+4) +'.png' )
      plt.clf()

      code_num +=1

      dfs = pd.concat([dfs,rest_df],axis=1)
   return dfs




def get_mongo_last_date(cal_day):
 ### mongo query for last ? days
 dictt_set = [ {"$group": { "_id" : { "$toInt" : "$date" } }},{"$sort" : {"_id" :-1}} , { "$limit" : cal_day},{"$sort" : {"_id" :1}} , { "$limit" :1}]

 ### mongo dict data

 set_doc =  read_aggregate_mongo('bankrate','daily_currency',dictt_set)

 ### for lists  get cal date 
 for idx in set_doc:

  idx_date = idx.get("_id")

 #set_date = str(idx_date)
 return str(idx_date)




### data_collections= 'currency_rate_' + format_str

avg_price_df = avg_daily_currency(data_collections)
## select column 

df_com = df_com.iloc[: , [1,3,6]]



### get insert mongo before last price 
last_price_df.rename(columns={'_id': 'code'},inplace=True)

last_price_df = last_price_df.astype({"last_now":"float"})

### merge data , add last_price_df check duplicate the same price 

avg_price_com_dfs = pd.merge(avg_price_df,df_com  , on = ['code'],how='left')
avg_price_dfs = pd.merge(avg_price_com_dfs,last_price_df , on = ['code'],how='left')

avg_price_dfs.rename(columns={'現金賣':'now'}, inplace=True)

line_avg_price_dfs = avg_price_dfs.copy()

avg_price_dfs['chk'] = avg_price_dfs.apply(lambda x: x['code'] if x['avg'] > x['now'] and x['now'] != x['last_now']  else None ,axis =1 )

### avg > now(down)  NT  rise up :  a lot money income to stock
### avg < now(up)    NT  down : a lot money out of stock
## filter ['chk'] is None 

avg_price_dfs = avg_price_dfs.dropna(axis=0) 
avg_price_dfs = avg_price_dfs.iloc[:,[0,1,2,3]]

notify_line_time ='18:00:00'
## line notify work on stock time 0900~1330
if not avg_price_dfs.empty and time.strftime("%H:%M:%S", time.localtime()) < notify_line_time  :

   #match_row_5(get_updatetime,avg_price_dfs,"\n ")
   match_row_5( " \n "+get_updatetime,avg_price_dfs," [NT Rise Up] \n")


if not match_row.empty  :

      match_row_5(" \n "+ get_updatetime,match_row,"  [Target]  \n ")



#print('dfs_low:',dfs_low)

### into daily_currency_low && line
if not dfs_low.empty :
         for idx in range(len(dfs_low)) :
             ## insert to daily_currency_low  
             records = [{ 'code' :dfs_low.loc[idx]['code'], 'bank_rate_sell':dfs_low.loc[idx]['現金賣'], 'last_modify': datetime.datetime.now()}]
             #records = records.to_dict(orient='records')
             del_dic = {'code' :dfs_low.loc[idx]['code'] }

             #print('records:', records)
             #print('del_dic:', del_dic)
             delete_many_mongo_db('bankrate','daily_currency_low',del_dic)
             insert_many_mongo_db('bankrate','daily_currency_low',records)

             insert_redis_data('daily_currency_low',dfs_low.loc[idx]['code'],dfs_low.loc[idx]['現金賣'])

         dfs_low =dfs_low.iloc[:,[0,1,3]]
         match_row_5(get_updatetime,dfs_low,"   [Daily_Low] \n")



#bank_close_time ='14:30:00'
bank_close_time ='18:30:00'

dd_f = datetime.date.today().strftime('%Y%m%d')
#print('dd_f:',dd_f ,'data_collections:',data_collections)

### into daily_currency && line 
if   time.strftime("%H:%M:%S", time.localtime()) > bank_close_time :
      

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
       match_row.rename(columns={'_id':'code'}, inplace=True) 
       records = match_row.copy()
       records['date'] = dd_f 
       records = records.iloc[:,[0,1,2,3,5,4]]
       #print(records.info())
       records = records.to_dict(orient='records')
       ### mongo daily_currency count(*)
       dicct_chk =  [
                { "$match" :{ "date":dd_f }},
                { "$group": { "_id" : "null" ,
                             "count" : { "$sum" : 1 }
                           }
                }
                ]

       mongo_doc_chk = read_aggregate_mongo('bankrate','daily_currency',dicct_chk)
       mongo_doc_count =  pd.DataFrame(list(mongo_doc_chk))
       
       ### check mongo is empty of insert    
       if mongo_doc_count.empty  :
          
         
          insert_many_mongo_db('bankrate','daily_currency',records)

          ### line nodify 
          match_row = match_row.iloc[:,[0,1,2,3]]
          #match_row.rename(columns={'_id':'code'}, inplace=True)
          avg_price_dfs = line_avg_price_dfs.iloc[:,[0,1,3]]
          ### avg > now(down)  NT  rise up :  a lot money income to stock
          ### avg < now(up)    NT  down : a lot money out of stock

          match_row =  pd.merge(match_row,avg_price_dfs  , on = ['code'],how='left')     
          match_row['NT_rise'] = match_row.apply(lambda x: '[Up]' if x['avg'] > x['now']  else '[Null]' if   x['avg'] == x['now'] else '[Down]' ,axis =1 )
          match_row_5("\n"+get_updatetime,match_row,"\n ")



          ### email on saturday
          if datetime.datetime.today().isoweekday() == 6 :  ## show all without filter on friday

             ### del images/*.png
             del_png.del_images()

             ### get last day 
             ddate = get_mongo_last_date(60)

             dictt = {}
             _columns= {"code":1,"_id":0}
             code_lists = []
             mydoc = read_mongo_db('bankrate','target_currency',dictt,_columns)
             for idx in mydoc :
                 code_lists.append(idx.get('code'))

             mail_match_row = Plot_Exchange_Rate(ddate,code_lists)
             #Plot_Exchange_Rate(ddate,code_lists)
  
             body = mail_match_row.to_html(classes='table table-striped',escape=False)

             send_mail.send_email('Exchange_Rate_{today}'.format(today=dd_f),body)

       

else  :
   print("%s target_currency is not match buy_price" % get_updatetime)
   print(match_df) 
