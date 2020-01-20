#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

## chromedrive 2.32

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
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
from selenium.webdriver.common.action_chains import ActionChains
import re
import redis

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='awa_login_with_reply.log',
		    filemode='a')


logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))


url="https://awabest.com/forum.php"
#url2="https://awabest.com/plugin.php?id=awa_signin" ##user_singnin of week
#url3='https://awabest.com/awa_signin-sign.html'
#bt_hd_url="https://apk.tw/forum-883" ##BT HD page
#bt_hd_url="https://apk.tw/forum-883-1.html" ##BT HD page
#https://apk.tw/thread-884337-1-1.html
#url_credit = 'https://apk.tw/home.php?mod=spacecp&ac=credit'
## id:dcsignin_tips
url_credit = 'https://awabest.com/home.php?mod=spacecp&ac=credit&showcredit=1'
reply_history_p1 ='https://apk.tw/home.php?mod=space&'
reply_history_p2 ='&do=thread&view=me&type=reply&from=space'

today_week = datetime.date.today().strftime("%w")

#logger = logging.getLogger(bt_hd_url)
#logger.info("BT HD page !!")

### Usage Virtual Dispaly
display = Display(visible=0, size=(800, 600))
display.start()
#web = webdriver.Chrome()
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path

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

    return myusername_list , mypassword_list , uid_list

def get_redis_data():

    #docker exec -it my-redis redis-cli LRANGE myreply_history_j20180702 0 -1
    myusername_list = r.lrange('awa_myusername_list','0','-1')
    mypassword_list = r.lrange('awa_mypassword_list','0','-1')
    uid_list = r.lrange('awa_uid_list','0','-1')

    return myusername_list , mypassword_list , uid_list





###  Reply Format 
def reply_format(): 
    reply_str_all =[]
    today = time.strftime('%Y/%m/%d' , time.localtime())
    download_speed = str(random.randrange(300, 1000,1))+'kb/s'
    
    feedback =[
    '非常推薦~在電影院看的~非常刺激',
    '純推~在電影院看的~非常好看',
    '感覺很刺激~感謝版大分享',
    '感謝版主分享~下載去',
    '感恩~感恩！給大大強力推推囉！感謝大大分享！',
    '萬般期待終於等到 感謝版主分享',
    '感謝版主分享~下載中',
    '看起來好似不錯感謝大大的分享!',
    '謝謝分享，終於等到好畫值，讚啦',
    '感恩超級期待這片!收藏了...感謝版主',
    '自己下載檔案影片 不小心刪除 , 重新下載一次 , 感謝版主分享',
    '看過預告片,劇情好像蠻不錯.....感謝分享!!!',
    '評價很不錯,絕無冷場,很緊湊的一部好戲,感謝分享!',
    '終於等到好的字幕，假日可以好好欣賞，謝謝大大的分享。',
    '畫質還不錯,感謝大大的分享.',
    '我很喜歡的劇情、精彩的片段 , 謝謝分享']
        
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
    if int(today_week) > 5 :
            ran_rows = random.randrange(3,7,1) ## get non-repetitive random 2~5 rows from get_link_list
    else :
            ran_rows = random.randrange(2,4,1) ## get non-repetitive random 2~5 rows from get_link_list
    ## got page list random page num 
    page_num_list=random.sample(list(range(10,25)), k=ran_rows)

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
    
def myreply_history(myusername,myreply_history_url,log_file):
    
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
    try :
         all_page_myreply_tids = str_split_2(myreply_history_list) 
         with open(log_file,'w') as fp :
              for h_list in all_page_myreply_tids : 
                  fp.write(h_list + '\n')
    finally :
             fp.close()

    return all_page_myreply_tids


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


### Get emot id 
def get_emot_id(web):
    ###find(name,attrs,recursive,text,**wargs)
    emotid_list = []
    soup = BeautifulSoup(web.page_source, "html.parser")
    dcsignin2_list = soup.find_all('div', attrs={'class': re.compile('dcsignin2')})  ## find out signin icon
    for dcsignin2 in dcsignin2_list :
        img_list = dcsignin2.find('img')  ## record img data
        emotid_list.append(img_list.get('id'))  ##record  emotid id values
    
    ran_rows = random.randrange(0, len(emotid_list), 1)  ## get random id
    return emotid_list[ran_rows]

### Login User Page
## get user & pwd 
#myusername_list , mypassword_list , uid_list = get_config() ## get loging user && pwd 
myusername_list , mypassword_list , uid_list = get_redis_data() ## get loging user && pwd 

for num in range(len(myusername_list)):
    myusername=myusername_list[num] 
    mypassword =mypassword_list[num]
    #myreply_history_url = reply_history_p1+ uid_list[num] + reply_history_p2
    #log_file = 'myreply_history_'+myusername+'.log'    
 
    #web = webdriver.Chrome() ## for cron path	
    web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path	
    web.get(url)
    time.sleep(random.randrange(3, 5, 1))

    web.find_element_by_id("ls_username").send_keys(myusername)
    web.find_element_by_id("ls_password").send_keys(mypassword)
    web.find_element_by_xpath("//button[contains(@class, 'pn vm')]").submit() ## login
    logger = logging.getLogger(myusername)
    logger.info("login botton is successed")
    time.sleep(random.randrange(2, 10, 1))
 
    ### click signature btn of dcsignin_tips
    signature_url = WebDriverWait(web, 15).until(EC.element_to_be_clickable((By.ID, 'dcsignin_tips')))  ###  top signature button of login form
    signature_url.click() ## page jump
    logger.info("signature botton is successed")
    time.sleep(random.randrange(2, 5, 1))
    #logger.info("singture botton is not exist")

    try : ### get random emot_id
         emot_id = get_emot_id(web)
         logger_emot_id = logging.getLogger(emot_id)
         logger_emot_id.info("emot_id got is successed!!")  

    except :
           logger.info("emot_id got is failed or Already signature")
           break

    try:## prepare client info
        signframe = web.find_element_by_id('fwin_sign')
        postForm = web.find_element_by_id("signform")
        p_emot_id = web.find_element_by_id(emot_id)
        click_btn = web.find_element_by_xpath("//button[@name='signpn']") 
        ### mouse clieck emot & btn 
        ActionChains(web).move_to_element(postForm).click(p_emot_id).click(click_btn).perform()
        time.sleep(random.randrange(5, 10, 1))
        logger = logging.getLogger(myusername)
        logger.info("signature is successed!!")

    except:
          logger.info("signature is failed!!")
          break 
  
    time.sleep(random.randrange(3, 10, 1)) 
   
    ### auto reply not yat 
    ###
    ###
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

if today_week == '1' :
     ### read for log last 47 line of mail body
     body = ''
     log_date = datetime.date.today().strftime("%Y-%m-%d")
     try:
          with open('awa_login_with_reply.log') as fp:
            data = fp.readlines()
            for i in data[-100:]:
              if log_date in i:  ## read only  today log 
                  body  = body + i
     
     finally:
         fp.close()
     
     
     send_mail.send_email('awalogin auto loging',body)

