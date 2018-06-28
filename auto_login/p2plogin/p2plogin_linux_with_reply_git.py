#! /usr/bin/Genv python3.6
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
import re

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='p2p_login_with_reply.log',
		    filemode='a')


logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

myusername_list =["XXXXXXXX","XXXXXXXX"] 
mypassword_list =["XXXXXXXX","XXXXXXXX"]   

url="http://www.p2p101.com/"
url2="http://www.p2p101.com/home.php?mod=task&amp;do=apply&amp;id=3" ##user_task_page
bt_hd_url="http://www.p2p101.com/forum.php?mod=forumdisplay&fid=920" ##BT HD page

## Usage Virtual Dispaly
display = Display(visible=0, size=(800, 600))
display.start()
#web = webdriver.Chrome()
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path

##  reply format 
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
    '感恩超級期待這片!收藏了...感謝版主']
        
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

##  Get BT HD page   
def get_link(bt_hd_url): 
    get_link_list= []
    link_str = []
    ## auto_reply
    web.get(bt_hd_url) ## login BT HD page 
    soup = BeautifulSoup(web.page_source , "html.parser")
    threadlist = soup.find(id='threadlisttableid')  ## get forum threadlist ID
    for normalthread_list  in threadlist.find_all('tbody',{'id':re.compile('^normalthread_')}):  ## match rows
        for td_list in normalthread_list.find_all('td',{'class':re.compile('icn')}):
            for link  in td_list.find_all('a'):  ##get link 
                get_link_list.append(link.get('href'))
            
    ### random get_link_list rows & thread_num                
    for rows in range(random.randrange(1,6,1)): ## get 1~5 rows
      #link_str.append(url+get_link_list[rows])
       thread_num = random.randrange(0,len(get_link_list),1) ##random thread_num
       link_str.append(url+get_link_list[thread_num])
    return link_str


## login user page

for num in range(len(myusername_list)):
    myusername=myusername_list[num] 
    mypassword =mypassword_list[num]
 
    #web = webdriver.Chrome() ## for cron path	
    web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path	
    web.get(url)
    time.sleep(1)
    web.find_element_by_id("ls_username").send_keys(myusername)
    web.find_element_by_id("ls_password").send_keys(mypassword)
    web.find_element_by_xpath("//button[contains(@class, 'pn vm')]").submit() ## login
    logging.info("login botton is success")
    
    time.sleep(random.randrange(1, 5, 1))

    #######  auto_reply
    auto_get_link_list = get_link(bt_hd_url) ## get BT_HD thread link list 
    for auto_link_str in auto_get_link_list :
        auto_reply = reply_format()
        ## threadlist page change
        web.get(auto_link_str)
        time.sleep(random.randrange(2, 5, 1))
        web.find_element_by_id("fastpostmessage").clear()
        web.find_element_by_id("fastpostmessage").send_keys(auto_reply) ## reply format_str on textarea
        time.sleep(random.randrange(2, 5, 1))
	              
        try :
             WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID, "fastpostsubmit"))).submit() ## textarea submit
             #print(auto_link_str,auto_reply)
             logger = logging.getLogger(auto_link_str)
             logger.info("textarea is successed ,waiting next link !!")
             time.sleep(random.randrange(10, 30, 1))	                              
        except :
               logger = logging.getLogger(auto_link_str)
               logger.info("textarea is failed!!")            	      	
               break
        
    ### chagne next link             
    web.quit()	          	          
    time.sleep(random.randrange(1, 5, 1))      
	               
    #######  login user task
    web.get(url2)
    time.sleep(random.randrange(1, 5, 1))

    ####### got redpackage 
    try: 
        link = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH, "//img[@alt='apply']")))
        link.click()
        logger = logging.getLogger(myusername)		
        logger.info("get redpackage is successed!!")
    except:
          logger = logging.getLogger(myusername)
          logger.info("link is not exist!!")
    ## close web 	
    time.sleep(random.randrange(1, 10, 1))
    web.quit()
          
    ## waiting next trun user
    if num < (len(myusername_list)-1):	
       logging.info("waiting for next  user!!")
       time.sleep(random.randrange(60, 180, 10))
    else :
          break

time.sleep(random.randrange(1, 10, 1))
logging.info("user all done!!")
display.stop()


## email on monday 

today_week = datetime.date.today().strftime("%w")

if today_week == '1' :
     ### read for log last 10 line of mail body
     body = ''
     try:
             with open('p2p_login_with_reply.log') as fp:
              data = fp.readlines()
              for i in data[-10:]:
               body  = body + i
     
     finally:
         fp.close()
     
     
     send_mail.send_email('p2plogin auto loging',body)

