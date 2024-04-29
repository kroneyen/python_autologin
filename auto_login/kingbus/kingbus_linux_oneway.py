#! /usr/bin/env python3.7
# -*- coding: utf-8 -*-

## chromedrive 2.32
###20190128 adding customzied date funtion Check_sys_date 

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
#import datetime
from datetime import datetime , timedelta ## by datetime calss
from pyvirtualdisplay import Display #nodisplay on chrome
from selenium.common.exceptions import NoSuchElementException ## show error msg
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
from selenium.webdriver.support.ui import Select
import send_mail
import re

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='kingbus.log',
		    filemode='a')


logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))


#s_start_id ='A03' ##<option value="A03">台北轉運</option>
#s_end_id ='H26' ##<option value="H26">朝　　馬　</option>
##crontab for monday 
#day_from = datetime.datetime.strftime(datetime.today() + datetime.timedelta(days = 11),'%Y/%m/%d')  ## booking friday
#day_return = datetime.datetime.strftime(datetime.today() + datetime.timedelta(days = 14),'%Y/%m/%d') ## booking next monday     
"""
s_f_h ='18'
s_f_m ='50'
s_r_h ='06'
s_r_m ='00'
"""
def random_ticket():
  i = random.randrange(0,len(ticket_num),1)
  ticket_1 = ticket_num[i]
  if i == (len(ticket_num)-1) :
    ticket_2 = ticket_num[0]
  else :
    ticket_2 = ticket_num[i+1]

  return ticket_1 , ticket_2
"""
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
            elif section_list =='ticket':
               ticket_num = ast.literal_eval(config.get(section_list,key))
            elif section_list =='seat':
               seat_list = ast.literal_eval(config.get(section_list,key))


    return myusername_list , mypassword_list , ticket_num , seat_list
"""

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


def get_option_num(soup,tb_id,time) : 
###format '06:00     '
  table_id = soup.find('table',{'id':re.compile(tb_id)})  ## find table_id
  _tr_style_list = []
  tr_num =2  ## counter _tr_style_list index_start 
  j =0    ## check find out tag
  tr_num_0=0

  ### 4 tr_style  
  for _tr_style in table_id.find_all('tr',{'style':re.compile('^color:Black')}):  ## find tr_style  of 3
      _tr_style_list.append(_tr_style)
  
  ### 3 schdule time tr num from 2 
  for _td_list in _tr_style_list :
      _td_resverve = _td_list.find('td',{'align':re.compile('right')}).string  ## find resverve num
      for _td in _td_list.find_all('td',{'align':re.compile('center')}) :   ## find td string match time
          if _td.string == time and int(_td_resverve) > 0 :  ## check time & resverve free
            j =1
            break

          if _td.string == time and int(_td_resverve) == 0 :
             tr_num_0 = tr_num
           
      if j == 0 and tr_num <5:
          tr_num =tr_num +1
      else :
            break

  return tr_num ,time ,tr_num_0


### execute python with sys argv 
#def Check_sys_date(s_day_from , s_day_return) :
def Check_sys_date(s_day_from ) :
    import sys
    try :
          s_day_from = sys.argv[1]
          #s_day_return = sys.argv[2]

    except :
           print('please execute python with sys_argv')
           sys.exit(1)

    if s_day_from == '0' :
       day_from = datetime.strftime(datetime.today() + timedelta(days = 7),'%Y/%m/%d')  ## booking friday
       #day_from = datetime.strftime(datetime.today() + timedelta(days = 14),'%Y/%m/%d')  ## booking friday
       #day_from = datetime.datetime.strftime(datetime.today() + datetime.timedelta(days = 11),'%Y/%m/%d')  ## booking friday
    else :
       day_from = s_day_from

     
    return day_from 
    """
    if s_day_return == '0' :
       day_return = datetime.datetime.strftime(datetime.today() + datetime.timedelta(days = 14),'%Y/%m/%d') ## booking next monday
    else :
       day_return = s_day_return

    return day_from , day_return
    """

### choice  seat
def change_seat(num):
    seat_from = 'ctl00_ContentPlaceHolder1_ckb1A'  ## from_seat
    seat_return = 'ctl00_ContentPlaceHolder1_ckb1B'  ## return_seat
    num = int(num)  ## str trans to int

    if num < 10:
        order_seat_from = seat_from + '0' + str(num)
        order_seat_return = seat_return + '0' + str(num)
    else:
        order_seat_from = seat_from + str(num)
        order_seat_return = seat_return + str(num)

    return order_seat_from, order_seat_return

### word replace of '*'
def mark_word(word):
    str = ''
    for nw in range(len(word)) :
       if nw >0 and  nw < (len(word) -3) :
          str = str + '*'
       else :
          str = str + word[nw]

    return str


#order_url="https://order.kingbus.com.tw/ORD/ORD_M_1520_OrderGoBack.aspx"
order_url="https://order.kingbus.com.tw/ORD/ORD_M_1510_OrderGo.aspx"

## Usage Virtual Dispaly
#display = Display(visible=0, size=(800, 600))
display = Display(visible=0, size=(1280, 800))
display.start()
#web = webdriver.Chrome()
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path

## step 1
## get user & pwd
#myusername_list , mypassword_list , ticket_num  , seat_list = get_config() ## get loging user && pwd && search & booking time
myusername_list , mypassword_list , ticket_num  , seat_list , hkey_lists,m_to= get_redis_data() ## get loging user && pwd && search & booking time form redis 
## customize booking date
day_from  = Check_sys_date(None)
#day_from , day_return = Check_sys_date(None,None)
        

## mutiple user booking
for u_num in range(len(myusername_list)):
      myusername=myusername_list[u_num]
      mypassword =mypassword_list[u_num]
      ##### search & booking time for user
      b_f_time = []
      b_r_time = []
      #print(keys)
      hkey_lists_data = hkey_lists[mypassword] ### mapping user phone_num to booing info
      #print(hkey_lists_data)
      for  field_key  in  hkey_lists_data :
          if re.compile('b_f_time').match(field_key):
              b_f_time.append(hkey_lists_data[field_key])
          elif re.compile('b_r_time').match(field_key):
              b_r_time.append(hkey_lists_data[field_key])                      
          elif field_key == 's_f_time_h':
              s_f_h = hkey_lists_data[field_key]
          elif field_key == 's_f_time_m':
              s_f_m = hkey_lists_data[field_key]
          elif field_key == 's_r_time_h':
              s_r_h = hkey_lists_data[field_key]
          elif field_key == 's_r_time_m':
              s_r_m = hkey_lists_data[field_key]
          elif field_key == 's_start_id':
              s_start_id = hkey_lists_data[field_key]
          elif field_key == 's_end_id':
              s_end_id = hkey_lists_data[field_key]                
          #elif field_key == 'm_to':
          #    m_to.append(hkey_lists_data[field_key])         
              
      web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path
      web.get(order_url)
      time.sleep(random.randrange(3, 5, 1))
      web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCustomer_ID").send_keys(myusername)
      web.find_element_by_id("ctl00_ContentPlaceHolder1_txtPhone").send_keys(mypassword)
      time.sleep(random.randrange(3, 5, 1))
      web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep1_OK").click()
      time.sleep(random.randrange(3, 5, 1))
      logger_mw = logging.getLogger(mark_word(myusername_list[u_num]))
      div_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_UsrMsgBox_txtMsg").text
      b_num =0  ### booking times
      while (b_num < 1) :
             if (len(div_msg) == 0) :
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
             today_week = str(datetime.strptime(day_from,'%Y/%m/%d').isoweekday()) ## str to weekday (1~7)
             #today_week = datetime.today().strftime("%w")

             if today_week == '1' :  ## switch from & distance for return
                s_oneway_r_from_id = s_end_id 
                s_oneway_r_to_id = s_start_id 
                s_start_id = s_oneway_r_from_id 
                s_end_id = s_oneway_r_to_id 

             try :
                   Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlStation_ID_From")).select_by_value(s_start_id)
                   logging.info("From_location  is success")
                   time.sleep(random.randrange(3, 5, 1))
             except : 
                     #logging.info("From_location  is failed")
                     #web.save_screenshot('From_location_failed.png')
                    
                     div_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_UsrMsgBox_txtMsg").text 
                     web.save_screenshot('%s_From_location_failed.png' % mark_word(myusername_list[u_num]))
                     logging.info(div_msg)
                     
                     break
             
             try :
                   Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlStation_ID_To")).select_by_value(s_end_id)
                   logging.info("Destination_location  is success")
                   time.sleep(random.randrange(3, 5, 1))
             except : 
                     div_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_UsrMsgBox_txtMsg").text
                     logging.info(div_msg)
                     web.save_screenshot('%s_Destination_location_failed.png' % mark_word(myusername_list[u_num]))
             
                     break
      
             ### choice station  from date , rutern date
             logger_day_from = logging.getLogger(day_from)
             try :
                  web.find_element_by_id("ctl00_ContentPlaceHolder1_txtOut_Dt").send_keys(day_from)
                  #web.find_element_by_id("ctl00_ContentPlaceHolder1_txtAOut_Dt").send_keys(day_from)
                  logger_day_from.info("From Date choose  is success")
                  time.sleep(random.randrange(3, 5, 1))
             except :
                     #web.find_element_by_id("ctl00_ContentPlaceHolder1_txtAOut_Dt").send_keys(day_from) 
                     logger_day_from.info("From Date choose  is failed")
             	     #alert_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_UsrMsgBox_txtMsg").text
                     #alert_msg = web.switch_to_alert().text ### get alert msg
                     #web.switch_to_alert().accept() ### get alert msg
                     #alert_msg = web.switch_to_alert().text() ### get alert msg
                     #logger_day_from.info(alert_msg)
                     web.save_screenshot('%s_From_Date_choose_failed.png' % mark_word(myusername_list[u_num]))
                     break             
             """       
             logger_day_return = logging.getLogger(day_return)
             try :
                  web.find_element_by_id("ctl00_ContentPlaceHolder1_txtBOut_Dt").send_keys(day_return)
                  logger_day_return.info("Return Date choose  is success")
                  time.sleep(random.randrange(3, 5, 1))
             except : 
                     logger_day_return.info("Return Date choose  is failed")
                     web.save_screenshot('%s_Return_Date_choose_failed.png' % mark_word(myusername_list[u_num]))
                     break
             """ 
             if today_week == '1' :
                ### list 
                
                s_f_h = s_r_h
                s_f_m = s_r_m
             
             ### search from time table 18:50 page
             time_from = s_f_h + ':' +s_f_m
             logger_time_from = logging.getLogger(time_from)
             try :
                  Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlHour")).select_by_value(s_f_h)
                  #Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlAHour")).select_by_value(s_f_h)
                  time.sleep(random.randrange(3, 5, 1))
                  Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlMinute")).select_by_value(s_f_m)
                  #Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlAMinute")).select_by_value(s_f_m)
                  time.sleep(random.randrange(3, 5, 1))
                  logger_time_from.info("Search From Time choose is success")
             except : 
                     logger_time_from.info("Search From Time choose is failed")
                     web.save_screenshot('%s_SearchFromTime_failed.png' % mark_word(myusername_list[u_num]))
                     time.sleep(random.randrange(1, 3, 1))
                     break
             """
             ### search return time table 06:00 page
             time_return = s_r_h + ':' + s_r_m
             logger_time_return = logging.getLogger(time_return)
             try :
                  Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlBHour")).select_by_value(s_r_h)
                  time.sleep(random.randrange(3, 5, 1))
                  Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlBMinute")).select_by_value(s_r_m)
                  time.sleep(random.randrange(3, 5, 1))
                  logger_time_return.info("Search Return Time choose is success")
             except :
                     logger_time_return.info("Search Return Time choose is failed")
                     web.save_screenshot('%s_Search_ReturnTime_failed.png' % mark_word(myusername_list[u_num]))
                     time.sleep(random.randrange(1, 3, 1))
                     break
            """
             ### search time table button
             
             try :
                  WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnStep2_OK"))).click()
                  time.sleep(random.randrange(20, 30, 1))    ### waiting for 3 schdule table
                  logging.info("step2_next_click search time table   is success")
             
             except :
                     logging.info("step2_next_click search time table is failed")
                     web.save_screenshot('%s_SearchTime_failed.png' % mark_word(myusername_list[u_num]))
                     time.sleep(random.randrange(1, 3, 1))
                     break
             ### step 3
             ### for get_option_num
             soup = BeautifulSoup(web.page_source  , "html.parser")
             
             ## check from time table  1st: 18:55  , 2nd: 18:45 ,3rd : 19:15
             f_condi =''
             list_n=0
             f_o_num=5
             #from_time_list=['18:55     ','18:45     ','19:15     ']
             #from_time_list=['18:55     ','18:45     ']
             if today_week == '1' :
                b_f_time = b_r_time
                 
             while (list_n < len(b_f_time) and f_o_num ==5) :
                         
                    f_o_num , f_o_time , f_o_num_0 = get_option_num(soup,'ctl00_ContentPlaceHolder1_grdList',b_f_time[list_n])
                    #f_o_num , f_o_time , f_o_num_0 = get_option_num(soup,'ctl00_ContentPlaceHolder1_grdAList',b_f_time[list_n])
                    #print (f_o_num , f_o_time , f_o_num_0)
                    list_n +=1
             
             if (f_o_num < 5) :
                    f_condi="//*[@id='ctl00_ContentPlaceHolder1_grdList']/tbody/tr["+ str(f_o_num) +"]/td[2]/input"
                    #f_condi="//*[@id='ctl00_ContentPlaceHolder1_grdAList']/tbody/tr["+ str(f_o_num) +"]/td[2]/input"
             else : 
                    f_condi_0="//*[@id='ctl00_ContentPlaceHolder1_grdList']/tbody/tr["+ str(f_o_num_0) +"]/td[2]/input"
                    #f_condi_0="//*[@id='ctl00_ContentPlaceHolder1_grdAList']/tbody/tr["+ str(f_o_num_0) +"]/td[2]/input"
             
             
             try :
                 from_botton = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.XPATH, f_condi)))
                 from_botton.click()
                 time.sleep(random.randrange(5, 10, 1))
                 logger_f_o_time=logging.getLogger(f_o_time)
                 logger_f_o_time.info("step3_click_1 check from time table  is success")
             
             except:
                   #f_condi="//*[@id='ctl00_ContentPlaceHolder1_grdAList']/tbody/tr["+ str(f_o_num_0) +"]/td[2]/input"
                   from_botton = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.XPATH, f_condi_0)))
                   from_botton.click()
                   time.sleep(random.randrange(5, 10, 1))
                   logger_f_o_time=logging.getLogger(f_o_time)
                   #logger_f_o_time.info("step3_click_1 check from time table  is failed")
                   div_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_UsrMsgBox_txtMsg").text             
                   logger_f_o_time.info(div_msg)
                   web.save_screenshot('%s_Check_from_time_failed.png' % mark_word(myusername_list[u_num]))
                   break
             """
             ## check return time table
             r_condi =''
             list_n=0
             r_o_num=5
             while (list_n < len(b_r_time) and r_o_num ==5) :
             #r_o_num,r_o_time =get_option_num(soup,'ctl00_ContentPlaceHolder1_grdBList','06:00     ')
                r_o_num,r_o_time ,r_o_num_0 =get_option_num(soup,'ctl00_ContentPlaceHolder1_grdBList',b_r_time[list_n])
                list_n +=1
             
             if (r_o_num < 5) :
                   r_condi="//*[@id='ctl00_ContentPlaceHolder1_grdBList']/tbody/tr["+ str(r_o_num) +"]/td[2]/input"
             else : 
                   r_condi_0="//*[@id='ctl00_ContentPlaceHolder1_grdBList']/tbody/tr["+ str(r_o_num_0) +"]/td[2]/input"   
             
             logger_r_o_time=logging.getLogger(r_o_time)
             
             try:
                 return_botton = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.XPATH, r_condi)))
                 return_botton.click()
                 time.sleep(random.randrange(5, 10, 1))
                 #logger_r_o_time=logging.getLogger(r_o_time)
                 logger_r_o_time.info("step3_click_2 check return time table is success")
             
             except:
                   #r_condi="//*[@id='ctl00_ContentPlaceHolder1_grdBList']/tbody/tr[3]/td[2]/input"
                   return_botton = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.XPATH, r_condi_0)))
                   return_botton.click()
                   time.sleep(random.randrange(5, 10, 1))
                   #logger_r_o_time=logging.getLogger(r_o_time)
                   div_msg = web.find_element_by_id("ctl00_ContentPlaceHolder1_UsrMsgBox_txtMsg").text
                   logger_r_o_time.info(div_msg)
                   #logger_r_o_time.info("step3_click_2 check return time table is failed")
                   web.save_screenshot('%s_Check_return_time_failed.png' % mark_word(myusername_list[u_num]))
                   break
             """
             ### check time table button
             try:
                 step3_click = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnStep3_OK")))
                 step3_click.click()
                 time.sleep(random.randrange(3, 5, 1))
                 logging.info("step3_next check time table button  is success")
             
             except:
                   logging.info("step3_next check time table button  is failed")
                   #web.save_screenshot('%s_CheckTimeTable_failed.png' % mark_word(myusername_list[u_num]))
                   break
             
             ### step 4
             ### for loop choice seat
             j=0
             k=99
             #k=0
             f_s_num=''
             r_s_num=''
             #seat_list_seq = ['8','6','7','11','9','10','14','12','13']
             for s_num in seat_list:  ##seat num from seat_list
                  order_seat_from,order_seat_return = change_seat(s_num)
             
                  ### choice from seat
                  if j < len(seat_list) :
                       try:
                             from_seat = WebDriverWait(web, 5).until(EC.element_to_be_clickable((By.ID, order_seat_from)))
                             from_seat.click()
                             j = 99  ## got seat
                             logger_num1 = logging.getLogger(s_num)
                             logger_num1.info("choice seat_from num1 is sucesses")
                             f_s_num=s_num
                             time.sleep(random.randrange(2, 5, 1))
             
                       except:
                              j = j+1
                              if j >= len(seat_list):
                                 logging.info("choice seat_from seat is full")
                                 web.save_screenshot('%s_Seat_from_full.png' % mark_word(myusername_list[u_num]))
                                 break  ### set is full 
             
                  """
                  ### choice return seat
             
                  if k < len(seat_list) :
                       try:
                           return_seat = WebDriverWait(web, 5).until(EC.element_to_be_clickable((By.ID, order_seat_return)))
                           return_seat.click()
                           k = 99
                           logger_num2 = logging.getLogger(s_num)
                           logger_num2.info("choice return_seat num2 is sucesses")
                           r_s_num=s_num
                           time.sleep(random.randrange(2, 5, 1))
                       except:
                              k = k+1
                              if k >= len(seat_list):
                                 logging.info("choice seat_return seat is full")
                                 web.save_screenshot('%s_Seat_return_full.png' % mark_word(myusername_list[u_num])) 
                                 break
                  """
                  ##  choice seat is all done
             
                  if j == 99 and k == 99:
                    break
             
             #### choice radio ticket 
             if j == 99 and k == 99: # choice sucesses
                     ##radio
                     ###choice ticket amount:1
                     try:
                         web.find_element_by_id('ctl00_ContentPlaceHolder1_rblTot_Count_0').click()
                         #web.find_element_by_id('ctl00_ContentPlaceHolder1_rdoATot_Count_0').click()
                         time.sleep(random.randrange(1, 5, 1))
                         logging.info("setting form ticket amount is sucesses")
                         ## choice return ticket  count
                     except :
                             logging.info("setting from ticket amount is failed")
                             web.save_screenshot('%s_Set_from_ticket_amount_failed.png' % mark_word(myusername_list[u_num]))
                     """             
                     try:
                           web.find_element_by_id('ctl00_ContentPlaceHolder1_rdoBTot_Count_0').click()
                           time.sleep(random.randrange(1, 5, 1))
                           logging.info("setting return ticket amount is sucesses")
             
                     except :
                             logging.info("setting return ticket amount is failed")
                             web.save_screenshot('%s_Set_return_ticket_failed.png' % mark_word(myusername_list[u_num]))
                     """
                     ### finshed book bus ticket
                     try :
                          step4_click = web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep4_OK")
                          step4_click.click()
                          time.sleep(random.randrange(3, 5, 1))
                          logging.info("step4_click booking  ticket  is success")
             
                     except :
                             logging.info("step4_click book  ticket btn is failed")
                             web.save_screenshot('%s_Booking_ticket_failed.png' % mark_word(myusername_list[u_num]))
                             break


                     ### new alert msg fix 

                     try :
                          step5_0_click = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_UsrMsgBox_btnOK")))
                          step5_0_click.click()
                          logging.info("step5_0 alert msg btn is sucesses")
                          time.sleep(random.randrange(3, 5, 1))

                     except :
                             logging.info("tep5_0 alert msg btn is failed")
                             web.save_screenshot('%s_tep5_0_failed.png' % mark_word(myusername_list[u_num]))
                             break
                     

                     ### step 5 payment keyin ticket num
                     j = 0
                     k = 99
                     for t_num in range(len(ticket_num)):
                         from_ticket ,return_ticket = random_ticket()
                         time.sleep(random.randrange(3, 5, 1))
                         ## payment key ticket no1
             
                         if j < len(ticket_num):
                              try:
                                  web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCoupon_TicketNo1").send_keys(from_ticket)
                                  logger1 = logging.getLogger(from_ticket)
                                  logger1.info("step5_1 TicketNo1 keys in is sucesses")
                                  time.sleep(random.randrange(3, 5, 1))
                                  j = 99
             
                              except:
                                        if j < 99 :
                                         j = j+1
             
                         elif j == len(ticket_num) :
                                logging.info("step5_1 TicketNo1 from_ticket is faild")
                                break
                         """
                         ## payment key ticket no5
                         if k < len(ticket_num) :
                             try:
                                 web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCoupon_TicketNo5").send_keys(return_ticket)
                                 logger2 = logging.getLogger(return_ticket)
                                 logger2.info("step5_2 TicketNo5 keys in is sucesses")
                                 time.sleep(random.randrange(3, 5, 1))
                                 k = 99
             
                             except:
                                        if k < 99 :
                                         k = k +1
             
                         elif k == len(ticket_num) :
                                logging.info("step5_2 TicketNo5 return_ticket is faild")
                                break
                         """
                          
                         if j == 99 and k == 99 :
                            break
             
                     ## payment button
                     try :
                          pay_click = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnPayByPrepaidTickets")))
                          pay_click.click()
                          logger_mw = logging.getLogger(mark_word(myusername_list[u_num]))
                          logger_mw.info("Booking & Payment is Success")
                          if today_week == '5' :
                            logger_mw.info("%s " ,  "Day_From: " + day_from + '    F_seat: ' + f_s_num +  '    F_time: ' + f_o_time)
                          else :
                            day_return = day_from 
                            r_s_num = f_s_num
                            r_o_time = f_o_time  
                            logger_mw.info("%s " ,  "Day_Return: " + day_return + '    R_seat: ' + r_s_num +  '    R_time: ' + r_o_time) 
                          web.save_screenshot('%s_Booking&Payment_Success.png' % mark_word(myusername_list[u_num]))
             
                     except:
                            logging.info("step5_click payment btn is faild")
                            web.save_screenshot('%s_Payment_failed.png' % mark_word(myusername_list[u_num]))
                            break
             
             else :
                   logging.info("choice seat is all full") 
                   #u_num = len(myusername_list) ## choice seat is all full 
                   break ## choice seat is all full  while (b_num)
                  
             b_num +=1  ### user booking done
            
      ### Waiting next trun user && checked 

      if u_num < (len(myusername_list)-1):
           logging.info("waiting for next  user!!")
           time.sleep(random.randrange(60, 180, 10))
      else :
           break
      

web.quit()
display.stop()

body = ''
log_date = datetime.today().strftime("%Y-%m-%d")
try:
    with open('kingbus.log') as fp:
      data = fp.readlines()
      for i in data[-100:]:
          if log_date in i:  ## read only  today log 
             body  = body + i

finally:
    fp.close()

send_mail.send_email('kingbus auto booking ',body,m_to)
