#! /usr/bin/env python3.7
# -*- coding: utf-8 -*-

## chromedrive 2.32
###20190128 adding customzied date funtion Check_sys_date 

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from pyvirtualdisplay import Display #nodisplay on chrome
from selenium.common.exceptions import NoSuchElementException , UnexpectedAlertPresentException ## show error msg
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
from selenium.webdriver.support.ui import Select
import send_mail
import re
import kingbus_linux


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='kingbus.log',
		    filemode='a')


logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))



def get_redis_data():
    import redis
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
    r = redis.StrictRedis(connection_pool=pool)
    hkey_lists = {}
    m_to=[]
    myusername_list = r.lrange('kingbus_myusername_list','0','-1')
    mypassword_list = r.lrange('kingbus_mypassword_list','0','-1')
    ticket_num = r.lrange('kingbus_ticket_num','0','-1')
    seat_list = r.lrange('kingbus_seat_list','0','-1')
    for i in  mypassword_list :  ### get search & booking time for user
       hkey_list = r.hgetall(i)
       if len(hkey_list) >0 :
         hkey_lists[i] =hkey_list
         m_to.append(r.hget(i,'m_to'))

    return myusername_list , mypassword_list , ticket_num , seat_list ,hkey_lists,m_to



### execute python with sys argv 
def Check_sys_date(s_day_from , s_day_return) :
    import sys
    try :
          s_day_from = sys.argv[1]
          s_day_return = sys.argv[2]

    except :
           print('please execute python with sys_argv')
           sys.exit(1)

    if s_day_from == '0' :
       
       day_from = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days = 11),'%Y/%m/%d')  ## booking at friday con job on 1
       #day_from = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days = 14),'%Y/%m/%d')  ## booking at friday   con job on 5
    else :
       day_from = s_day_from

    if s_day_return == '0' :
       day_return = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days = 14),'%Y/%m/%d') ## booking next monday
       #day_return = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days = 17),'%Y/%m/%d') ## booking next at monday
    else :
       day_return = s_day_return

    return day_from , day_return



def alert_sw(web):
    try :
         alert_sw = web.switch_to.alert
         alert_msg = alert_sw.text
         alert_sw.accept()
    except : 
            alert_msg =''

    return alert_msg




order_url="https://order.kingbus.com.tw/ORD/ORD_M_1540_ViewOrder.aspx"

## Usage Virtual Dispaly
#display = Display(visible=0, size=(800, 600))
display = Display(visible=0, size=(1280, 800))
display.start()

## step 1
## get user & pwd
myusername_list , mypassword_list , ticket_num  , seat_list , hkey_lists,m_to= get_redis_data() ## get loging user && pwd && search & booking time form redis 
        

## mutiple user booking
for u_num in range(len(myusername_list)):
      myusername=myusername_list[u_num]
      mypassword =mypassword_list[u_num]
      ##### search & booking time for user
      b_f_time = []
      b_r_time = []
      #print(keys)
      hkey_lists_data = hkey_lists[mypassword] ### mapping user phone_num to booing info
              
      web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path
      web.get(order_url)
      time.sleep(random.randrange(3, 5, 1))
      web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCustomer_ID").send_keys(myusername)
      web.find_element_by_id("ctl00_ContentPlaceHolder1_txtPhone").send_keys(mypassword)
      time.sleep(random.randrange(3, 5, 1))
      web.find_element_by_id("ctl00_ContentPlaceHolder1_btnQuery").click()
      time.sleep(random.randrange(3, 5, 1))
      logger_mw = logging.getLogger(mark_word(myusername_list[u_num]))
      div_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_updStep2").text
      b_num =0  ### booking times
      while (b_num < 1) :
             if (len(div_msg) > 0) :
                  #div_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_UsrMsgBox_txtMsg").text
                  #web.save_screenshot('Login_failed.png')  
                  logger_mw.info("user login is success")
                  
             else :
                     logger_mw.info(div_msg)
                     web.save_screenshot('%s_Login_failed.png' % mark_word(myusername_list[u_num]))
                     break
             #logging.info("step1_next_click user login is success")
             
             ### step 2
             
             ### choice station  from Taipei_bus_center to Chaoma terminal
             try :
                   grdOrderList = web.find_element_by_id("ctl00_ContentPlaceHolder1_grdOrderList")
                   logging.info("grdOrderList  is success")
                   time.sleep(random.randrange(3, 5, 1))
             except : 
                     #logging.info("From_location  is failed")
                     #web.save_screenshot('From_location_failed.png')
                    
                     div_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_UsrMsgBox_txtMsg").text 
                     web.save_screenshot('%s_From_location_failed.png' % mark_word(myusername_list[u_num]))
                     logging.info(div_msg)
                     
                     break
             
             soup = BeautifulSoup(web.page_source, 'html.parser')
             td_list=[]
             today =  datetime.date.today().strftime("%Y%m%d")
             ### order records 
             if grdOrderList : 

                table_id = soup.find('table',{'id': "ctl00_ContentPlaceHolder1_grdOrderList"})  ## find table_id 

                for tr in table_id.find_all('tr') :
                    for td in tr.find_all('td',{'style':re.compile("white-space")}) :
                        td_list.append(td.text)                                           
                    
                    if len(td_list) > 0 :
                       order_date = td_list[0].split('_',1)[0]
                       if order_date != today : 
                          print(order_date)
                          #30 05  * * 1 cd /root/python_dir/kingbus && rm -rf *.png && /usr/local/bin/python3.6 kingbus_linux.py 0 0

             b_num +=1 

web.quit()
display.stop()

"""
body = ''
log_date = datetime.date.today().strftime("%Y-%m-%d")
try:
    with open('kingbus.log') as fp:
      data = fp.readlines()
      for i in data[-100:]:
          if log_date in i:  ## read only  today log 
             body  = body + i

finally:
    fp.close()

send_mail.send_email('kingbus auto booking ',body,m_to)

"""
