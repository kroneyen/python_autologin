#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

## chromedrive 2.32

from selenium import webdriver
#from selenium.webdriver.common.keys import Keys
import time
import datetime
from pyvirtualdisplay import Display #nodisplay on chrome
from selenium.common.exceptions import NoSuchElementException ## show error msg
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import send_mail
from bs4 import BeautifulSoup
import re
import redis

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='p2p_login_with_reply_software.log',
		    filemode='a')


logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))


url="http://www.p2p101.com"
url2="http://www.p2p101.com/home.php?mod=task&amp;do=apply&amp;id=3" ##user_task_page
bt_software_url="http://www.p2p101.com/forum.php?mod=forumdisplay&fid=33&page=" ##BT software page PS:Credit > 15
url_credit = 'http://www.p2p101.com/home.php?mod=spacecp&ac=credit&showcredit=1'
reply_history_p1 ='http://www.p2p101.com/home.php?mod=space&uid='
reply_history_p2 ='&do=thread&view=me&type=reply&order=dateline&from=space&page='
today_week = datetime.date.today().strftime("%w")


### Usage Virtual Dispaly
display = Display(visible=0, size=(800, 600))
display.start()
#web = webdriver.Chrome()
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path

### create redis connection pool 

pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.StrictRedis(connection_pool=pool)



def get_config():
    import configparser
    import ast

    config = configparser.ConfigParser()
    config.read('config.ini')
    for section_list in config.sections(): ## get  sctions
        for key in config[section_list] : ## get keys
            ## get values
            if section_list =='user':
               myusername_list = ast.literal_eval(config.get(section_list,key))
            elif section_list =='pwd':
               mypassword_list = ast.literal_eval(config.get(section_list,key))
            elif section_list =='uid':
               uid_list = ast.literal_eval(config.get(section_list,key))

    #return myusername_list[1:] , mypassword_list[1:] , uid_list[1:] ## return lists 1 after
    return myusername_list , mypassword_list , uid_list  ## return for all user

def get_redis_data():

    #docker exec -it my-redis redis-cli LRANGE myreply_history_j20180702 0 -1
    myusername_list = r.lrange('p2p_myusername_list','0','-1')
    mypassword_list = r.lrange('p2p_mypassword_list','0','-1')
    uid_list = r.lrange('p2p_uid_list','0','-1')

    return myusername_list , mypassword_list , uid_list





def reply_format():
    reply_str_all =[]
    today = time.strftime('%Y/%m/%d' , time.localtime())
    download_speed = str(random.randrange(0, 1000,1))+'kb/s'
    #download_speed = str(0)+'kb/s'

    feedback =[
    '正在學習電腦中 看起來很不錯謝謝~大大~分享',
    'thanks for your share!!!!!',
    '正好需要用到… 感謝分享!!!!',
    '感謝版主分享 ,學習應用!!! ',
    '下載研究看看 ,正在學習中, 感謝分享!! ',
    '很實用的軟體，謝謝樓主分享!!',
    '終於找到版本了~~ 感謝大大提供這個資訊供大家分享。'
    ]

    reply_format = [
    '下載日期 : ' ,
    '下載方式： BT' ,
    '下載速度 : ' ,
    '解壓方式： 無 ' ,
    '問題反饋： 無 ' ,
    '觀看感受 : ' ]

    for i in range(len(reply_format)) :
        if i ==0 :
         #print(reply_format[i],today)
         reply = reply_format[i]
         reply_str = reply + today
         reply_str_all.append(reply_str)
        elif i == 2 :
         #print(reply_format[i],download_speed) 
         reply = reply_format[i]
         reply_str = reply + download_speed
         reply_str_all.append(reply_str)
        elif i ==  5:
         #print(reply_format[i],feedback[random.randrange(1, len(feedback),1 )])
         reply = reply_format[i]
         reply_str = reply + feedback[random.randrange(1, len(feedback),1 )]
         reply_str_all.append(reply_str)
        else :
         #print(reply_format[i])
         reply = reply_format[i]
         reply_str = reply
         reply_str_all.append(reply_str)
    ## lists modle change to string line modle & return  
    format_str =''
    for sstr in reply_str_all:
        format_str = format_str + sstr + '\n'

    return  format_str  ##return reply format 





###  Get BT HD page   
def get_link(ori_bt_hd_url,today_week):

    get_link_list= []
    if int(today_week) > 5 or int(today_week) == 0 :
            ran_rows = random.randrange(3,5,1) ## get non-repetitive random 2~5 rows from get_link_list
    else :
            ran_rows = random.randrange(2,4,1) ## get non-repetitive random 2~5 rows from get_link_list
    ## got page list random page num 
    page_num_list=random.sample(list(range(1,40)), k=ran_rows)

    ### each page got  ran_rows
    for page_num in page_num_list :
        bt_hd_url=ori_bt_hd_url+str(page_num)
        ### Login BT HD page
        web.get(bt_hd_url) ## login BT HD page
        time.sleep(random.randrange(1, 2, 1))
        logger = logging.getLogger(bt_hd_url)
        logger.info("BT HD page !!")
        soup = BeautifulSoup(web.page_source , "html.parser")
        ### Get BR HD link
        threadlist = soup.find(id='threadlisttableid')  ## get forum threadlist ID
        for normalthread_list  in threadlist.find_all('tbody',{'id':re.compile('^normalthread_')}):  ## match rows
              for td_list in normalthread_list.find_all('td',{'class':re.compile('icn')}):
                  for link  in td_list.find_all('a'):  ##get all link
                      get_link_list.append(link.get('href'))

        time.sleep(random.randrange(1, 3, 1))

    ### check non-repetitive link list
    return get_link_list,ran_rows


    
def myreply_history(myusername,myreply_history_url,log_file_key):
    
    myreply_history_list = []
    time.sleep(random.randrange(1, 2, 1))
    logger = logging.getLogger(myusername)
    logger.info("login myreply history page !!")
    ### Get Myreply_history all_page lists
    page_num =1
    while 1 :
             try  :
                   web.get(myreply_history_url+str(page_num))
                   soup_2 = BeautifulSoup(web.page_source , "html.parser") 
                   form_table = soup_2.find(id='delform')
                   for link_2 in  form_table.find_all('a',{'title':re.compile('新窗口打開')}):
                       myreply_history_list.append(link_2.get('href'))
                   ### next myreply page 
                   WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "nxt")))
                   time.sleep(random.randrange(1, 3, 1))
                   page_num = page_num +1 
             except :
                    break
    ### first time lists write into log file
    try :## get  my history tid list from redis
         all_page_myreply_tids = str_split_2(myreply_history_list)
         for sstr in all_page_myreply_tids :
             r.rpush(str(log_file_key),str(sstr)) ## first time redis insert key(log_file) values(tid=xxxxx)
         logger = logging.getLogger(myusername)
         logger.info("first time get myreply history page all done !!")


    except :
             logger = logging.getLogger(myusername)
             logger.info('my_history first time is failed !!!')
#break

    return all_page_myreply_tids

    """
    try :
         all_page_myreply_tids = str_split_2(myreply_history_list) 
         with open(log_file,'w') as fp :
              for h_list in all_page_myreply_tids : 
                  fp.write(h_list + '\n')
    finally :
             fp.close()

    return all_page_myreply_tids
    """

### Split HD tid
def str_split_1(sttr_list) :
   str_split_list=[]
   for sttr in sttr_list :
       row_str_split=sttr.split('viewthread&')
       row_str_split_2 =row_str_split[1].split('&extra')
       str_split_list.append(row_str_split_2[0])
   return str_split_list

### Splist my reply history tid 
def str_split_2(sttr_list) :
   str_split_list=[]
   for sttr in sttr_list :
       row_str_split=sttr.split('viewthread&')
       row_str_split_2 =row_str_split[1].split('&highlight=')
       str_split_list.append(row_str_split_2[0])
   return str_split_list

### Splist '\n'
def str_split_3(sttr_list) :
   str_split_list=[]
   for sttr in sttr_list :
       row_str_split=sttr.split('\n')
       str_split_list.append(row_str_split[0])
   return str_split_list


###check  tid auto_reply && myreply 
def chk_reply_tid(rep_link_list,all_page_lists_tids,ran_rows) :
    link_str = []
    log_file_tids = []
    random.shuffle(rep_link_list) ## random list seq
    chk_rep_tid_list = str_split_1(rep_link_list)
    chk_myreply_history_tid_list = all_page_lists_tids
    ### check tid not in exist  myreply_history lists
    k=0
    ### check exclude on all_page_lists_tids link list
    for elem in chk_rep_tid_list :
        if elem not in chk_myreply_history_tid_list:  ### not in the lists , will be write into log file
             if len(log_file_tids) < ran_rows:
                link_str.append(rep_link_list[k]) ##link_str to list
                log_file_tids.append(elem)  ## tid to list
             else :
                   break
        k+=1
    #non_rep_link_list = random.sample(get_link_list, k=ran_rows)
    ## return exclude link_str of myreply_history_tid_list
    return link_str,log_file_tids


### Get User Credit To Log Records
def get_credit(myusername):
    web.get(url_credit)
    soup = BeautifulSoup(web.page_source , "html.parser")
    credit = soup.find('ul',{'class':re.compile('creditl mtm bbda cl')})
    for li_list  in credit.find_all('li'):
     logger = logging.getLogger(myusername)
     logger.info(li_list.text)


### Login User Page
#myusername_list , mypassword_list , uid_list = get_config() ## get loging user && pwd
myusername_list , mypassword_list , uid_list = get_redis_data() ## get redis loging user && pwd

for num in range(len(myusername_list)):
    myusername=myusername_list[num] 
    mypassword =mypassword_list[num]
    myreply_history_url = reply_history_p1+ uid_list[num] + reply_history_p2
    #log_file = 'myreply_history_'+myusername+'.log'    
    log_file_key = 'myreply_history_'+myusername    
 
    #web = webdriver.Chrome() ## for cron path	
    web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path	
    web.get(url)
    time.sleep(random.randrange(1, 5, 1))
    web.find_element_by_id("ls_username").send_keys(myusername)
    web.find_element_by_id("ls_password").send_keys(mypassword)
    web.find_element_by_xpath("//button[contains(@class, 'pn vm')]").submit() ## login
    logger = logging.getLogger(myusername)   
    logger.info("login botton is success")
    time.sleep(random.randrange(1, 5, 1))

    ### Get User myreply_history lists
    """
    ### try to open myreply log_file , if is exist 
    try :
          with open(log_file) as rp:
               row_data = rp.readlines()
               all_page_lists_tids = str_split_3(row_data) ### get tid lists from log file
          rp.close()
    except : 
            ## first times data list is empty 
            all_page_lists_tids  = myreply_history(myusername,myreply_history_url,log_file)  ## from all_page_lists_tids
    """
    ### get my history log all tid
    try :
          if r.llen(log_file_key) > 0 : ### redis key len
             all_page_lists_tids = r.lrange(log_file_key,'0','-1')

    except :
            ## first times data list is empty 
            all_page_lists_tids  = myreply_history(myusername,myreply_history_url,log_file_key)  ## from all_page_lists_tids
    ### check auto_get_link_list avoid get_link result is 0
    while 1 :
             auto_get_link_list = []
             rep_link_list,ran_rows = get_link(bt_hd_url,today_week) ### Get auto_reply_link
             chk_link_list , log_file_tids=  chk_reply_tid(rep_link_list,all_page_lists_tids,ran_rows)  ## check auto_reply_link avoid is exist in  myreply_history
             #non_rep_link_list = get_link(bt_hd_url,today_week) ### Get auto_reply_link          
             #chk_link_list , log_file_tids=  chk_reply_tid(non_rep_link_list,all_page_lists_tids)  ## check auto_reply_link avoid is exist in  myreply_history

             if len(chk_link_list) > 0 :  ### non-repetitive reply link more than the 1
                for str_link in chk_link_list :
                   auto_get_link_list.append(url + str_link)  ### full link addr
                break
    ###  Auto_Reply 
    log_tids_num = 0 
    #with open(log_file,'a') as chkp:
    for auto_link_str in auto_get_link_list :
            auto_reply = reply_format()
            ## threadlist page change
            web.get(auto_link_str)
            time.sleep(random.randrange(1, 5, 1))
            try : 
                 web.find_element_by_id("fastpostmessage").clear()
                 web.find_element_by_id("fastpostmessage").send_keys(auto_reply) ## reply format_str on textarea
                 time.sleep(random.randrange(1, 5, 1))
                 WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID, "fastpostsubmit"))).submit() ## textarea submit
                 #print(auto_link_str,auto_reply)
                 ###write into log files 
                 #chkp.write(log_file_tids[log_tids_num] + '\n') ## write tids to myhistory file
                 ### write into redis key 
                 r.rpush(str(log_file_key),str(log_file_tids[log_tids_num]))
                 log_tids_num = log_tids_num +1
                 logger = logging.getLogger(auto_link_str)
                 logger.info("reply is successed ,waiting next link !!")
                 time.sleep(random.randrange(10, 30, 1))                                  

            except :
                    logger = logging.getLogger(auto_link_str)
                    logger.info("reply is failed!!")                         
                    break

    #chkp.close()
    logger = logging.getLogger(myusername)
    logger.info("reply all done!!") 
    time.sleep(random.randrange(1, 5, 1))     
    ###  Login user task 
    web.get(url2)
    time.sleep(random.randrange(1, 5, 1))

    ### Got redpackage 
    try: 
        link = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH, "//img[@alt='apply']")))
        link.click()
        logger = logging.getLogger(myusername)		
        logger.info("get redpackage is successed!!")
    except:
          logger = logging.getLogger(myusername)
          logger.info("link is not exist!!")

    ### Get Credit info && close web 
    get_credit(myusername)
    time.sleep(random.randrange(1, 10, 1))
    web.quit()
          
    ### Waiting next trun user
    if num < (len(myusername_list)-1):	
       logging.info("waiting for next  user!!")
       time.sleep(random.randrange(60, 180, 10))
    else :
          break

time.sleep(random.randrange(1, 10, 1))
logging.info("user all done!!")
display.stop()

### Send Email on monday 

#today_week = datetime.date.today().strftime("%w")

#if today_week == '1' :
     ### read for log last 47 line of mail body
body = ''     
try:
      with open('p2p_login_with_reply_software.log') as fp:
           data = fp.readlines()
           for i in data[-47:]:
             body  = body + i

finally:
         fp.close()


send_mail.send_email('p2plogin_software auto loging',body)

