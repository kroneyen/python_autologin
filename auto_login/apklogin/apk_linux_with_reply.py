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
import traceback

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='apk_login_with_reply.log',
		    filemode='a')


logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))


url="https://apk.tw/forum.php"
short_url='https://apk.tw/'
url2="https://apk.tw/home.php?mod=task&do=view&id=7" ##user_task_page of week
bt_hd_url="https://apk.tw/forum-883-" ##BT HD page
#bt_hd_url="https://apk.tw/forum-883-1.html" ##BT HD page
#https://apk.tw/thread-884337-1-1.html
url_credit = 'https://apk.tw/home.php?mod=spacecp&ac=credit'
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
def get_link(bt_hd_url,today_week):
    page_num = random.randrange(10,45,1)
    bt_hd_url=bt_hd_url+str(page_num)+'.html'  ## apk BT_URL page format
    get_link_list= []

    ### Login BT HD page 
    web.get(bt_hd_url) ## login BT HD page
    time.sleep(random.randrange(1, 2, 1))
    logger = logging.getLogger(bt_hd_url)
    logger.info("BT HD page !!")
    soup = BeautifulSoup(web.page_source , "html.parser")
    ### Get BT HD link 
    threadlist = soup.find(id='threadlisttableid')  ## get forum threadlist ID
    for normalthread_list  in threadlist.find_all('tbody',{'id':re.compile('^normalthread_')}):  ## match rows
        for td_list in normalthread_list.find_all('td',{'class':re.compile('icn')}):
            for link  in td_list.find_all('a'):  ##get all link
                get_link_list.append(link.get('href'))
    ### check non-repetitive link list
    #today_week = datetime.date.today().strftime("%w")

    if int(today_week) > 5 :
            ran_rows = random.randrange(3,7,1) ## get non-repetitive random 2~5 rows from get_link_list
    else :
            ran_rows = random.randrange(2,4,1) ## get non-repetitive random 2~5 rows from get_link_list

    non_rep_link_list = random.sample(get_link_list, k=ran_rows)
    return non_rep_link_list
    
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
### EXP: thread-894449-1-1.html
def str_split_1(sttr_list) :
   str_split_list=[]
   for sttr in sttr_list :
       row_str_split=sttr.split('-1')
       str_split_list.append(row_str_split[0])
   return str_split_list

### Splist my reply history tid  for first time
### EXP : <a href="thread-879396-1-1.html" title="新窗口打開" target="_blank">  
def str_split_2(sttr_list) :
   str_split_list=[]
   for sttr in sttr_list :
       row_str_split=sttr.split('-1')
       str_split_list.append(row_str_split[0]) ### thread-879396
   return str_split_list

### Splist '\n'
def str_split_3(sttr_list) :
   str_split_list=[]
   for sttr in sttr_list :
       row_str_split=sttr.split('\n')
       str_split_list.append(row_str_split[0])
   return str_split_list


###check  tid auto_reply && myreply 
def chk_reply_tid(non_rep_link_list,all_page_lists_tids) :
    link_str = []
    log_file_tids = []
    chk_non_rep_tid_list = str_split_1(non_rep_link_list)
    chk_myreply_history_tid_list = all_page_lists_tids
    ### check tid not in exist  myreply_history lists
    k=0 
    for elem in chk_non_rep_tid_list :
        if elem not in chk_myreply_history_tid_list:  ### not in the lists , will be write into log file
           link_str.append(non_rep_link_list[k])
           log_file_tids.append(elem) 
        k = k +1   
    
    return link_str,log_file_tids


### Get User Credit To Log Records
def get_credit(myusername):
    web.get(url_credit)
    soup = BeautifulSoup(web.page_source , "html.parser")
    credit = soup.find('ul',{'class':re.compile('creditl mtm bbda cl')})
    for li_list  in credit.find_all('li'):
     logger = logging.getLogger(myusername)
     logger.info(li_list.text)


### Get check vaild answer 
def get_ans(sttr):
   row_str_split=str(sttr).split('？【')
   row_str_split_2 =row_str_split[1].split('】')
   return row_str_split_2[0]



### Login User Page
## get user & pwd 
myusername_list , mypassword_list , uid_list = get_config() ## get loging user && pwd 

for num in range(len(myusername_list)):
    myusername=myusername_list[num] 
    mypassword =mypassword_list[num]
    myreply_history_url = reply_history_p1+ uid_list[num] + reply_history_p2
    log_file = 'myreply_history_'+myusername+'.log'    
 
    #web = webdriver.Chrome() ## for cron path	
    web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path	
    web.get(url)
    time.sleep(random.randrange(3, 5, 1))

    ### hidden form 
    loginForm  = web.find_element_by_class_name("mousebox")                                                                                                   
    fromname   = web.find_element_by_css_selector(".mousebox  #ls_username")                                                                                  
    frompwd   = web.find_element_by_css_selector(".mousebox #ls_password")                                                                                    
    click_btn =web.find_element_by_xpath("//*[@id='lsform']/div/div/button/em")                                                                               
    #click_btn =web.find_element_by_xpath("//button[contains(@class, 'pn vm')]")                                                                              
    ### mouse move to element loging
    try :
         ActionChains(web).move_to_element(loginForm).send_keys_to_element(fromname,myusername).send_keys_to_element(frompwd,mypassword).click(click_btn).perform()
         logger = logging.getLogger(myusername)
         logger.info("login botton is success")
         time.sleep(random.randrange(5, 10, 1))
         
    except :  
            logger = logging.getLogger(myusername)
            logger.info("login botton is success")
            break

    ### Got signature 
    try:
        signature = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID,"my_amupper")))
        signature.click()
        logger = logging.getLogger(myusername)
        logger.info("signature is successed!!")
    except:
          logger = logging.getLogger(myusername)
          logger.info("signature is not exist!!")

    time.sleep(random.randrange(3, 10, 1))


    ### try to open myreply log_file , if is exist 
    try :
          with open(log_file) as rp:
               row_data = rp.readlines()
               all_page_lists_tids = str_split_3(row_data) ### get tid lists from log file
          rp.close()
    except :
            ## first times data list is empty 
            all_page_lists_tids  = myreply_history(myusername,myreply_history_url,log_file)  ## from all_page_lists_tids

    ### check auto_get_link_list avoid get_link result is 0
    while 1 :
             auto_get_link_list = []
             non_rep_link_list = get_link(bt_hd_url,today_week) ### Get auto_reply_link          
             chk_link_list , log_file_tids=  chk_reply_tid(non_rep_link_list,all_page_lists_tids)  ## check auto_reply_link avoid is exist in  myreply_history

             if len(chk_link_list) > 1 :  ### non-repetitive reply link more than the 1
                for str_link in chk_link_list :
                   auto_get_link_list.append(short_url + str_link )  ### full link addr
                break
    ###  Auto_Reply   
    log_tids_num = 0
    with open(log_file,'a') as chkp:
        for auto_link_str in auto_get_link_list :
            auto_reply = reply_format()
            ## threadlist page change
            web.get(auto_link_str)
            #logger = logging.getLogger(auto_link_str)
            #logger.info("login reply page is success!!")
            time.sleep(random.randrange(1, 5, 1))
            web.find_element_by_id("fastpostmessage").clear()
            web.find_element_by_id("fastpostmessage").send_keys(auto_reply)
            fs_btn =web.find_element_by_id('fastpostsubmit')
            time.sleep(random.randrange(3, 5, 1))
            #logger.info(" reply fastpostmessage is success!!")
            """
            ActionChains(web).move_to_element(fs_btn).perform() ### mousemove btn
            time.sleep(random.randrange(2, 5, 1))           
            
            try :
                 ### display checkpost 
                 soup = BeautifulSoup(web.page_source , "html.parser")
                 seccheck_form = soup.find('div',{'id':re.compile('seccheck_fastpost')})
                 ### get anwser 
                 qa = str(seccheck_form.find('div',{'class':re.compile('p_pop p_opt')}))
                 ### spliting anwser sting   
                 ans = str(get_ans(qa))
                 ans_form = web.find_element_by_name('secanswer')
                 time.sleep(random.randrange(2, 5, 1))
                 ### post answer  to  checkpost
                 ActionChains(web).move_to_element(ans_form).send_keys_to_element(ans_form,ans).click(fs_btn).perform()
            """
            try :
                 ActionChains(web).click(fs_btn).perform()
                 time.sleep(random.randrange(3, 5, 1))
                 ### write tid to log_file 
                 chkp.write(log_file_tids[log_tids_num] + '\n')
                 log_tids_num = log_tids_num +1 ##@ trun tid next 
                 logger = logging.getLogger(auto_link_str)
                 logger.info("reply is successed ,waiting next link !!")
                 time.sleep(random.randrange(10, 30, 1))

            except :
                    logger = logging.getLogger(auto_link_str)
                    logger.info("reply is failed!!")
                    break

    chkp.close()
    logger = logging.getLogger(myusername)
    logger.info("reply all done!!")
    time.sleep(random.randrange(1, 5, 1))


    ### Got user task of 7 days
    ###  Login user task
    web.get(url2)
    time.sleep(random.randrange(1, 5, 1))

    try:

        link = WebDriverWait(web, 15).until(EC.element_to_be_clickable((By.XPATH, "//img[@alt='立即申請']")))
        link.click()
        logger = logging.getLogger(myusername)
        logger.info("get task of 7 Day is successed!!")
    except:
          logger = logging.getLogger(myusername)
          logger.info("task task of 7 Day is not exist!!")

    time.sleep(random.randrange(1, 5, 1))


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
     try:
             with open('apk_login_with_reply.log') as fp:
              data = fp.readlines()
              for i in data[-20:]:
               body  = body + i
     
     finally:
         fp.close()
     
     
     send_mail.send_email('apklogin auto loging',body)

