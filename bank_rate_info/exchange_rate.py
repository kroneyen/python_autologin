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
from io import StringIO
import os
import sys 
sys.path.append("..")
#from stock import del_png
from stock import tg_bot
import del_png 
#import tg_bot
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent


url = 'https://rate.bot.com.tw/xrt?Lang=zh-TW'

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.StrictRedis(connection_pool=pool)

### fake user agent
#user_agent = UserAgent()

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--user-agent=%s" % user_agent)
#options.add_argument("--disable-site-isolation-trials")
#options.add_argument("--renderer-process-limit=4")
web = webdriver.Chrome(options=options)






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


def send_tg_bot_msg(token,chat_id,msg):

  #url = f"https://api.telegram.org/bot{'+token+'}/sendMessage?chat_id={'+chat_id}&text={msg}&parse_mode=HTML"
  url = "https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={msg}&parse_mode=HTML".format(token = token ,chat_id=chat_id,msg=msg)

  try :
       requests.get(url)

  except :
       time.sleep(random.random()) ### 0~1 num   
       requests.get(url)



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
   
    r.hset(_key,diic)
    

def hmset_insert_redis_data(_key,dicct):

    #r.hmset(_key,dicct)
    ##  DeprecationWarning: Call to deprecated hmset. (Use 'hset' instead.) -- Deprecated since version 4.0.0.)
    r.hset(_key,mapping=dicct)


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
    try :
        if collection.count() > 0 :
            collection.drop()
    except :
        ### pymongo > =3.7
        if collection.count_documents({})  > 0 :
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


def ifnull(value, default):

   return value if value is not None else default


def get_exchange_rate() :


  web.get(url)
  time.sleep(5)
  soup = BeautifulSoup(web.page_source, 'html.parser')

  #print(soup)

  # Original line: get_updatetime = soup.find('span',{"class": "time"}).getText()
  # Fix: Check if the element is found before calling getText()

  time_element = soup.find('span',{"class": "time"})
  if time_element:
      get_updatetime = time_element.getText()
  else:
      #raise ValueError("Could not find the update time element (<span with class='time'>). The website structure might have changed.")
      get_updatetime = datetime.datetime.now()


  # Changed from r.text to web.page_source
  df = pd.pandas.read_html(StringIO(web.page_source))[0]
  currency_name= []
  currency_code= []
  
  #print(df.info())
  for i in range(len(df.iloc[:,0])) :

    arg_3 = df.iloc[:,0][i].split(' ',2)
    currency_name.append(arg_3[0])
    currency_code.append(arg_3[1].replace("(","").replace(")","")) 



  df['name']= currency_name
  df['code'] = currency_code
  
  ## atlas mongo
  _db ='bankrate'
  _collection='target_currency'
  _collection_low='daily_currency_low'
  dicct={}
  _columns={"_id":0,"last_modify":0}



  ##atlas  mongo
  try :
          mongo_mydoc = atlas_read_mongo_db(_db,_collection,dicct,_columns)
          mongo_mydoc_low  = atlas_read_mongo_db(_db,_collection_low,dicct,_columns)

  ### local mongo 
  except :
          mongo_mydoc = read_mongo_db(_db,_collection,dicct,_columns)
          mongo_mydoc_low  = read_mongo_db(_db,_collection_low,dicct,_columns)
          

  """

  ### local mongo 
  try : 
          mongo_mydoc = atlas_read_mongo_db(_db,_collection,dicct,_columns)
          mongo_mydoc_low  = atlas_read_mongo_db(_db,_collection_low,dicct,_columns)
          
  ##atlas  mongo
  except : 
          mongo_mydoc = atlas_read_mongo_db(_db,_collection,dicct,_columns)
          mongo_mydoc_low  = atlas_read_mongo_db(_db,_collection_low,dicct,_columns)
  """
  mongo_mydoc_df = pd.DataFrame(list(mongo_mydoc))
  mongo_mydoc_df_low = pd.DataFrame(list(mongo_mydoc_low))




  """
  ### get redis data
  daily_currency_low =[]
  code_list = []
  bank_rate_sell_list=[]  

  
  ## atlas mongo
  _db ='bankrate'
  _collection='target_currency'
  _collection_low='daily_currency_low'
  dicct={}
  _columns={"_id":0,"last_modify":0}
  
  ### atlas mongo 
  try : 
          mongo_mydoc = atlas_read_mongo_db(_db,_collection,dicct,_columns)
          
  ##local mongo
  except : 
          mongo_mydoc = read_mongo_db(_db,_collection,dicct,_columns)
  mongo_mydoc_df = pd.DataFrame(list(mongo_mydoc))

  ## chk get mongo data   need check code
  if not mongo_mydoc_df.empty :
        code_list = list(mongo_mydoc_df['code'])
        bank_rate_sell_list= list(mongo_mydoc_df['bank_rate_sell']) 
        for idx in code_list : 
            daily_currency_low.append() ## values get from local redi      
        ## local mongo compare altas mongodb 
        local_mongo = read_mongo_db(_db,_collection,dicct,_columns)
        local_mongo_df = pd.DataFrame(list(local_mongo))
        chk_mongo = mongo_mydoc_df.equals(local_mongo_df)
        ##insert local mongo & redis sync for target_currency
        if chk_mongo == False:
           if not  mongo_mydoc_df.empty :
              drop_mongo_db(_db,_collection)  ## drop local data 
              records= mongo_mydoc_df.copy()
              records['last_modify']= datetime.datetime.now()
              records = records.to_dict(orient='records')
              insert_many_mongo_db(_db,_collection,records)
        
              ##insert local redis
              delete_redis_data(_collection)
              records = { k: v for k, v in zip(code_list, bank_rate_sell_list) }
              hmset_insert_redis_data(_collection,records)
  
  else : ## get redis data 
        for curr_idx in  get_redis_data('target_currency','hkeys','NULL','NULL') :
            bank_rate_sell_list.append(get_redis_data('target_currency','hget',curr_idx,'NULL'))
            daily_currency_low.append(get_redis_data('daily_currency_low','hget',curr_idx,'NULL'))
            code_list.append(curr_idx)
  
  """
  #df = df.iloc[:,[18,19,1,2,9,10]] ##name ,code 現金 本行買入/賣出  , 即期  買入/賣出
  df = df.iloc[:,[17,18,1,2,3,4]] ##name ,code 現金 本行買入/賣出  , 即期  買入/賣出
  df.columns= llist(len(df.columns))
  code_list = mongo_mydoc_df['code']
  df = df[df[1].isin(code_list)] ##比對 
  
  ### KRW no spot_rate_buy , spot_rate_sell
  for  idx in [4,5] :
       df.iloc[:,idx] = df.iloc[:,idx].apply(lambda  x: 0 if x.strip() =='-' else x )

  df = df.astype({2:'float',3:'float',4:'float',5:'float'})
  df.columns = ['name','code', 'bank_rate_buy','bank_rate_sell','spot_rate_buy', 'spot_rate_sell']

  #df.columns = ['name','code', '現金買','現金賣','即期買', '即期賣'] 
  ### merge target bank_rate_sell 
  #df =  pd.merge(df, mongo_mydoc_df  , on = ['code'],how='left')
  #df.rename(columns={'bank_rate_sell' : 'target'}, inplace=True)

  ###  insert into mongo 
  ori =  datetime.datetime.strptime(get_updatetime, "%Y/%m/%d %H:%M")
  format_str = datetime.datetime.strftime(ori, "%Y%m%d")
  currency_rate_collection =  'currency_rate_' + format_str 
  ### delete mongo collection for yesterday 
  mydoc = getCollectionNames_mongo('bankrate') 
  coll_doc =  name_regex(mydoc)
  for idx in  coll_doc: 
      ### 保留最後一個
      if idx != currency_rate_collection : 
         drop_mongo_db('bankrate',idx)
 
  ### Before insert of get monog data last row
  #dicct = [  {"$group" : {"_id" : "$code" ,"last_now" : {"$last" : "$bank_rate_sell"}     }}]
  
  #last_price = read_aggregate_mongo('bankrate',_collections,dicct)
  #last_price_df = pd.DataFrame(list(last_price))
  #print('dfffff:',df)

  ### insert mongo bankrate data 
  records = df.copy()
  records['last_modify']  = datetime.datetime.now()
  #records.rename(columns={'現金買':'bank_rate_buy','現金賣':'bank_rate_sell','即期買':'spot_rate_buy','即期賣':'spot_rate_sell'}, inplace=True)
  records = records.iloc[:,1:]
  records = records.to_dict(orient='records')
  #print('recordscurrency_rate_20240624:',records)
  insert_many_mongo_db('bankrate',currency_rate_collection,records)
  



  ### compare Target / low  price 
  dfs = pd.DataFrame()
  df_com = pd.DataFrame()
  dfs_low = pd.DataFrame()
  
  df_target = pd.DataFrame()
  df_low = pd.DataFrame()

  if not mongo_mydoc_df.empty :
         mongo_mydoc_df.rename(columns={'bank_rate_sell' : 'my_target'}, inplace=True)


  if not mongo_mydoc_df_low.empty :
        mongo_mydoc_df_low.rename(columns={'bank_rate_sell' : 'my_low'}, inplace=True)

  df_target = df.merge(mongo_mydoc_df,how='inner',on='code')
  df_low =  df.merge(mongo_mydoc_df_low,how='inner',on='code')

  my_target = df_target.iloc[:,[1,6]]

  #print('df_low_342',df_low.info())


  df_target['target'] =  df_target.apply(lambda  x:  float(x['bank_rate_sell'])  if float(x['bank_rate_sell']) < float(x['my_target'])  else  None ,axis=1)
  df_low['low'] =  df_low.apply(lambda  x:  float(x['bank_rate_sell'])  if float(x['bank_rate_sell']) < float(x['my_low'])   else  None ,axis=1)
  # df_target ['name','code', 'bank_rate_buy','bank_rate_sell','spot_rate_buy', 'spot_rate_sell','my_target','target']  
  # df_low ['name','code', 'bank_rate_buy','bank_rate_sell','spot_rate_buy', 'spot_rate_sell','my_low','low'] 
  df_target = df_target.dropna(axis=0)
  df_low = df_low.dropna(axis=0)
  #print('df_target',df_target) 
  #print('df_low',df_low) 
  ### insert mongo db
  """
  if not  df_target.empty :

          code_list =  df_target['code']
          bank_rate_sell_list = df_target['target'] 

          dicct={"code": "$in": code_list}          
          delete_many_mongo_db(_db,_collection,dicct)

          records= df_target.iloc[:,[1,3]].copy()
          records = records.to_dict(orient='records')
          insert_many_mongo_db(_db,_collection,records)
        
          ##insert local redis
          delete_redis_data(_collection)
          records = { k: v for k, v in zip(code_list, bank_rate_sell_list) }
          hmset_insert_redis_data(_collection,records)
  """
  if not df_low.empty : 

          code_list =  df_low['code']
          bank_rate_sell_list = df_low['low']

          dicct={"code": {"$in": list(code_list)}}
          #print('dicct',dicct) 
          delete_many_mongo_db(_db,_collection_low,dicct)

          records= df_low.iloc[:,[1,3]].copy()
          records['last_modify'] =  datetime.datetime.now()
          records = records.to_dict(orient='records')
          insert_many_mongo_db(_db,_collection_low,records)

          ##insert local redis
          delete_redis_data(_collection_low)
          records = { k: v for k, v in zip(code_list, bank_rate_sell_list) }
          hmset_insert_redis_data(_collection_low,records)




  # df ['name','code', 'bank_rate_buy','bank_rate_sell','spot_rate_buy', 'spot_rate_sell']  
  #df_target['full'] = df_target[['name', 'code']].apply(' '.join, axis=1) ## list_8
  df_target['full'] = df_target[['name', 'code']].apply(lambda x: ' '.join(x.astype(str)), axis=1) ## list_8
  #df_low['full'] = df_low[['name', 'code']].apply(' '.join, axis=1) ## list_8
  df_low['full'] = df_low[['name', 'code']].apply(lambda x: ' '.join(x.astype(str)), axis=1) ## list_8
  # df_target ['name','code', 'bank_rate_buy','bank_rate_sell','spot_rate_buy', 'spot_rate_sell','my_target','target','full']  
  # df_low ['name','code', 'bank_rate_buy','bank_rate_sell','spot_rate_buy', 'spot_rate_sell','my_low','low',full] 
  
  #print(df.info())
  #df.columns= llist(len(df.columns))
  #print('df_target_402:',df_target.info())
  #print('df_low:',df_low.info())
  """
  df_target = df_target.iloc[:,[8,2,3,4,5,6]]
  df_low = df_low.iloc[:,[8,2,3,4,5,6]]
  column_name=['幣別', '現金買','現金賣','即期買', '即期賣','Target']
  column_name_low=['幣別', '現金買','現金賣','即期買', '即期賣','Low']
  df_target.columns = column_name
  df_low.columns = column_name_low
  """ 
  return get_updatetime , df_target   , df_low , df , currency_rate_collection , my_target


get_updatetime , df_target , df_low ,df ,data_collections , my_target  = get_exchange_rate()

web.quit()

def match_row_5 ( get_updatetime ,match_row,extend) : 

          line_key_list =[]
          tg_key_list=[]
          tg_chat_id=[]

          #line_key_list.append( get_redis_data('line_key_hset','hget','Exchange_Rate','NULL')) ## for exchange_rate (Stock_YoY/Stock/rss_google/Exchange_Rate)
          tg_key_list.append(get_redis_data('tg_bot_hset','hget','@stock_broadcast_2024bot','NULL')) ## for tg of signle
          tg_chat_id.append(get_redis_data('tg_chat_id','hget','stock_broadcast','NULL')) ## for tg of signle

          for match_row_index in range(0,len(match_row),5) :
              #msg = get_updatetime + "  " ## for line br
              #msg = get_updatetime  +"\n " + match_row.iloc[match_row_index:match_row_index+5,:].to_string(index = False)  ## for line notify msg 1000  character limit 
              msg = ' \n ' + get_updatetime + extend  + match_row.iloc[match_row_index:match_row_index+5,:].to_string(index = False)  ## for line notify msg 1000  character limit 
              tg_msg ="【Exchange_Rate】"+  msg

              ### for multiple line group
              ### line notify colse on '2025-03-31'
              """
              deadline_check = datetime.date.today().strftime("%Y-%m-%d")
              if  deadline_check <= '2025-03-31' :

                  for line_key in  line_key_list : ##
                      send_line_notify(line_key, msg)
                      time.sleep(random.randrange(1, 3, 1))
              """

              for tg_key in  tg_key_list : ## 
                  #send_tg_bot_msg(tg_key,tg_chat_id[0],tg_msg)
                  #tg_bot.send_tg_bot_photo(caption,tg_file)
                  tg_bot.send_tg_bot_msg(tg_msg)
                  time.sleep(random.randrange(1, 3, 1))
   


def avg_daily_currency(data_collection): 

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

    avg_price = read_aggregate_mongo(_db,data_collection,dictt_avg)

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
      #plt.savefig('./images/image_'+ code_idx +'_'+ str(idx+4) +'.png' )
      plt.savefig('./images/image_'+ code_idx  +'.png' )
      plt.clf()

      code_num +=1

      dfs = pd.concat([dfs,rest_df],axis=1) 
   dfs.fillna(0,inplace=True) 
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
##{"code" , "avg"}

## select column 
#print('df_547',df.info())

#df = df.iloc[: , [1,3]]


#print('df_info_560',df.info())
### get insert mongo before last price 
#last_price_df.rename(columns={'_id': 'code'},inplace=True)

#last_price_df = last_price_df.astype({'last_now':'float'})
#last_price_df['last_now'] = last_price_df['last_now'].astype(float)

### merge data , add last_price_df check duplicate the same price 

avg_price_dfs = pd.merge(df ,avg_price_df , on = ['code'],how='left')
#avg_price_dfs = pd.merge(avg_price_com_dfs,last_price_df , on = ['code'],how='left')

avg_price_dfs.rename(columns={'bank_rate_sell':'now'}, inplace=True)

line_avg_price_dfs = avg_price_dfs.copy()
#print('575_avg_price_dfs',avg_price_dfs)
#print('575line_avg_price_dfs',line_avg_price_dfs)


#print('df',df.info())
#print('avg_price_df',avg_price_df.info())
#print('avg_price_dfs',avg_price_dfs.info())

#avg_price_dfs['chk'] = avg_price_dfs.apply(lambda x: x['code'] if x['avg'] > x['now'] and x['now'] != x['last_now']  else None ,axis =1 )
avg_price_dfs['chk'] = avg_price_dfs.apply(lambda x: x['code'] if x['avg'] > x['now']   else None ,axis =1 )
#print('avg_price_dfs_575',avg_price_dfs)
### avg > now(down)  NT  rise up :  a lot money income to stock
### avg < now(up)    NT  down : a lot money out of stock
## filter ['chk'] is None 
### now > avg 
avg_price_dfs = avg_price_dfs.dropna(axis=0) 
#print('avg_price_dfs_582',avg_price_dfs.info())
#avg_price_dfs = avg_price_dfs.iloc[:,[0,1,2,3]]
#print('df_target_590',df_target.info())
#print('avg_price_dfs_590',avg_price_dfs.info())

avg_price_dfs = avg_price_dfs.iloc[:,[1,6,3]]
#print( avg_price_dfs)
#print(my_target)
avg_price_dfs = pd.merge( avg_price_dfs ,my_target , on = ['code'],how='left')
avg_price_dfs.rename(columns={'my_target':'target'}, inplace=True)


#line_avg_price_dfs = avg_price_dfs.copy()



#print('line_avg_price_dfs_587',line_avg_price_dfs)

notify_line_time ='18:00:00'
## TG notify work on stock time 0900~1330
### now > avg
if not avg_price_dfs.empty and time.strftime("%H:%M:%S", time.localtime()) < notify_line_time  :

   #match_row_5(get_updatetime,avg_price_dfs,"\n ")
   match_row_5( " \n "+get_updatetime,avg_price_dfs," [NT Rise Up] \n")

### now < Target
if not df_target.empty  :
      #print(df_target.info())
      df_target = df_target.iloc[:,[8,2,3,4,5,6]]
      #df_low = df_low.iloc[:,[8,2,3,4,5,6]]
      column_name=['幣別', '現金買','現金賣','即期買', '即期賣','Target']
      #column_name_low=['幣別', '現金買','現金賣','即期買', '即期賣','Low']
      df_target.columns = column_name
      #df_low.columns = column_name_low


      match_row_5(" \n "+ get_updatetime,df_target,"  [Target]  \n ")



#print('dfs_low:',df_low.info())

### into daily_currency_low && line
if not df_low.empty :

         records = df_low.iloc[:,[1,3]].copy()
         records['last_modify'] = datetime.datetime.now()        
         del_dic = {"code":{"$in": list(df_low.iloc[:,1]) }}
         records = records.to_dict(orient='records')

         #print('records:',records)
         delete_many_mongo_db('bankrate','daily_currency_low',del_dic)
         insert_many_mongo_db('bankrate','daily_currency_low',records)

         #df_low = df_low.iloc[:,[8,2,3,4,5,6]]
         df_low = df_low.iloc[:,[8,3,6]]
         #column_name_low=['幣別', '現金買','現金賣','即期買', '即期賣','Low']
         column_name_low=['幣別', 'Now','Low']
         #df_target.columns = column_name
         df_low.columns = column_name_low

         #df_low =df_low.iloc[:,[0,1,3]]
         match_row_5(get_updatetime,df_low,"   [Daily_Low] \n")



#bank_close_time ='09:30:00'
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
          #print('line_avg_price_dfs',line_avg_price_dfs.info())
          #avg_price_dfs = line_avg_price_dfs.iloc[:,[0,1,3]]
          #print('line_avg_price_dfs_711',line_avg_price_dfs.info())
          
          avg_price_dfs = line_avg_price_dfs.iloc[:,[1,6]]
          ### avg > now(down)  NT  rise up :  a lot money income to stock
          ### avg < now(up)    NT  down : a lot money out of stock
  
          


          #print('match_row_716',match_row)
          #print('avg_price_dfs_716',avg_price_dfs)
 
          match_row =  pd.merge(match_row,avg_price_dfs  , on = ['code'],how='left')     
          #print('pm_6',match_row.info())
          match_row['NT_rise'] = match_row.apply(lambda x: '[Up]' if x['avg'] > x['now']  else '[Null]' if   x['avg'] == x['now'] else '[Down]' ,axis =1 )


          #match_row_5("\n"+get_updatetime,match_row,"\n ")
          match_row_5("【Close_Bank】\n"+get_updatetime,match_row,"\n ")



          ### email on saturday
          if datetime.datetime.today().isoweekday() == 5  :  ## show all without filter on friday
          #if datetime.datetime.today().isoweekday() > 5  :  ## show all without filter on friday

             dir_path = os.path.dirname(os.path.abspath(__file__))+ '/images/*.png'

             ### del images/*.png
             del_png.del_images(dir_path)

             ### get last day 
             ddate = get_mongo_last_date(60)

             dictt = {}
             _columns= {"code":1,"_id":0}
             code_lists = []
             mail_code = []
             mydoc = read_mongo_db('bankrate','target_currency',dictt,_columns)
             for idx in mydoc :
                 code_lists.append(idx.get('code'))
                 mail_code.append(f'<a href="https://rate.bot.com.tw/xrt/quote/ltm/%s" target="_blank">%s</a>' %( idx.get('code') , idx.get('code') ))

             mail_match_row = Plot_Exchange_Rate(ddate,code_lists)
             mail_match_row.columns = mail_code
  
             body = mail_match_row.to_html(classes='table table-striped',escape=False)

             send_mail.send_email('Exchange_Rate_{today}'.format(today=dd_f),body)

             ### sned photo to tg
             image_paths=[]
             items = os.listdir("images")  ## os.listdir (path)  

             caption='【Exchange_Rate_{today}】'.format(today=dd_f)

             for names in items :
                if  names.endswith(".png") : ##find out * '.png' file
                   #image_paths.append(names)
                   #tg_bot.send_tg_media_group(image_paths)
                   #tg_file='./images'+ names
                   tg_file=os.path.dirname(os.path.abspath(__file__))+ '/images/' +names 
                   tg_bot.send_tg_bot_photo(caption,tg_file)

"""
else  :
   print("%s target_currency is not match buy_price" % get_updatetime)
   print(match_row) 
"""   
