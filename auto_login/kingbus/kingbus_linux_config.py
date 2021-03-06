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


s_start_id ='A03' ##<option value="A03">台北轉運</option>
s_end_id ='H26' ##<option value="H26">朝　　馬　</option>
##crontab for monday 
day_from = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days = 11),'%Y/%m/%d')  ## booking friday
day_return = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days = 14),'%Y/%m/%d') ## booking next monday
time_from_h ='18'
time_from_m ='50'
time_return_h ='06'
time_return_m ='00'

def random_ticket():
  i = random.randrange(0,len(ticket_num),1)
  ticket_1 = ticket_num[i]
  if i == (len(ticket_num)-1) :
    ticket_2 = ticket_num[0]
  else :
    ticket_2 = ticket_num[i+1]

  return ticket_1 , ticket_2

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

def get_option_num(soup,tb_id,time) : 
###format '06:00     '
  table_id = soup.find('table',{'id':re.compile(tb_id)})  ## find table_id
  _tr_style_list = []
  num =2  ## counter _tr_style_list index_start 
  j =0    ## check find out tag

  for _tr_style in table_id.find_all('tr',{'style':re.compile('^color:Black')}):  ## find tr_style  of 3
      _tr_style_list.append(_tr_style)

  for _td_list in _tr_style_list :
      for _td in _td_list.find_all('td',{'align':re.compile('center')}) :   ## find td string match time
          if _td.string == time:
            j =1
            break
      if j == 0 and num <5:
          num =num +1
      else :
            break

  return num ,time


order_url="https://order.kingbus.com.tw/ORD/ORD_M_1520_OrderGoBack.aspx"

## Usage Virtual Dispaly
display = Display(visible=0, size=(800, 600))
display.start()
#web = webdriver.Chrome()
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path

## step 1
## get user & pwd
myusername_list , mypassword_list , ticket_num  , seat_list = get_config() ## get loging user && pwd

## mutiple user booking
for i in range(len(myusername_list)):
  myusername=myusername_list[i] 
  mypassword =mypassword_list[i]
  web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path	
  web.get(order_url)
  time.sleep(random.randrange(3, 5, 1))	
  web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCustomer_ID").send_keys(myusername)
  web.find_element_by_id("ctl00_ContentPlaceHolder1_txtPhone").send_keys(mypassword)
  time.sleep(random.randrange(3, 5, 1))
  web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep1_OK").click()
  time.sleep(random.randrange(3, 5, 1))

logging.info("step1_next_click  login is success")

### step 2

### choice station  from Taipei_bus_center to Chaoma terminal
Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlStation_ID_From")).select_by_value(s_start_id)

logging.info("From_location  is success")

time.sleep(random.randrange(3, 5, 1))
Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlStation_ID_To")).select_by_value(s_end_id)

logging.info("Destination_location  is success")
time.sleep(random.randrange(3, 5, 1))

### choice station  from date , rutern date
web.find_element_by_id("ctl00_ContentPlaceHolder1_txtAOut_Dt").send_keys(day_from)

time.sleep(random.randrange(3, 5, 1))

logging.info("From Date choose  is success")

web.find_element_by_id("ctl00_ContentPlaceHolder1_txtBOut_Dt").send_keys(day_return)

time.sleep(random.randrange(3, 5, 1))
logging.info("Return Date choose  is success")

### search from time table

Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlAHour")).select_by_value(time_from_h)
time.sleep(random.randrange(3, 5, 1))


Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlAMinute")).select_by_value(time_from_m)
time.sleep(random.randrange(3, 5, 1))

logging.info("From Time choose 18:55 is success")
### search return time table

Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlBHour")).select_by_value(time_return_h)
time.sleep(random.randrange(3, 5, 1))
Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlBMinute")).select_by_value(time_return_m)
time.sleep(random.randrange(3, 5, 1))

logging.info("Return Time choose 06:00 is success")

### search time table button

try :
     #step2_click = web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep2_OK")
     #step2_click.click()
     WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnStep2_OK"))).click()
     time.sleep(random.randrange(20, 30, 1))    ### waiting for 3 schdule table  
     logging.info("step2_next_click search time table   is success")

except : 
        web.quit()
        display.stop()
        logging.info("step2_next_click search time table is failed")

### step 3

### for get_option_num
soup = BeautifulSoup(web.page_source  , "html.parser")
#print('soup:',soup)
#id_page = soup.find_all('table',{'id':re.compile('^ctl00_ContentPlaceHolder1_grd')})
#print('id_page:',id_page) 

## check from time table
f_condi =''
f_o_num , f_o_time =get_option_num(soup,'ctl00_ContentPlaceHolder1_grdAList','18:55     ')

if f_o_num == 5 :
       f_o_num , f_o_time=get_option_num(soup,'ctl00_ContentPlaceHolder1_grdAList','18:45     ')

f_condi="//*[@id='ctl00_ContentPlaceHolder1_grdAList']/tbody/tr["+ str(f_o_num) +"]/td[2]/input"

try :
    #condi="//*[@id='ctl00_ContentPlaceHolder1_grdAList']/tbody/tr["+ str(o_num) +"]/td[2]/input"
    ##from_botton = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_grdAList']/tbody/tr[3]/td[2]/input")))
    from_botton = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.XPATH, f_condi)))
    from_botton.click() 
    time.sleep(random.randrange(3, 5, 1))
    #logger = logging.getLogger(_domian_list[i])
    #logger.info("domain confirm is successed!!")
    logger=logging.getLogger(f_o_time)
    logger.info("step3_click_1 check from time table  is success")
    #logging.info("step3_click_1 check from time table  is success")

except:
      web.quit()
      display.stop()
      logger=logging.getLogger(f_o_time)
      logger.info("step3_click_1 check from time table  is failed")
      #logging.info("step3_click_1 check from time table is failed")

## check return time table
r_condi =''
r_o_num,r_o_time =get_option_num(soup,'ctl00_ContentPlaceHolder1_grdBList','06:00     ')
r_condi="//*[@id='ctl00_ContentPlaceHolder1_grdBList']/tbody/tr["+ str(r_o_num) +"]/td[2]/input"

try:
    #return_botton = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_grdBList']/tbody/tr[3]/td[2]/input")))
    return_botton = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.XPATH, r_condi)))
    return_botton.click() 
    time.sleep(random.randrange(3, 5, 1))
    logger=logging.getLogger(r_o_time)
    logger.info("step3_click_2 check return time table is success")
    #logging.info("step3_click_2 check return time table is success")


except:
      web.quit()
      display.stop() 
      logger=logging.getLogger(r_o_time)
      logger.info("step3_click_2 check return time table is failed")
      #logging.info("step3_click_2 check return time table is failed")


### check time table button 
try:
    step3_click = WebDriverWait(web, 30).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnStep3_OK")))
    step3_click.click()
    time.sleep(random.randrange(3, 5, 1))	
    logging.info("step3_next check time table button  is success")

except:
      web.quit()
      display.stop()
      logging.info("step3_next check time table button  is failed")

   
#time.sleep(random.randrange(1, 3, 1))

### step 4

###choice  seat

def change_seat(num):
  seat_from='ctl00_ContentPlaceHolder1_ckb1A'  ## from_seat 
  seat_return='ctl00_ContentPlaceHolder1_ckb1B' ## return_seat 

  num = int(num)  ## str trans to int   

  if num < 10 :
   order_seat_from = seat_from+'0'+ str(num)
   order_seat_return = seat_return +'0' + str(num)
  else :
   order_seat_from = seat_from + str(num)
   order_seat_return = seat_return + str(num)
 
  return order_seat_from,order_seat_return

### for loop choice seat
j=0
k=0
#seat_list = ['8','6','7','11','9','10','14','12','13']

#for num in range(len(seat_list)):  ##seat num from seat_list 
for num in seat_list:  ##seat num from seat_list 
  order_seat_from,order_seat_return = change_seat(num)
  if j < len(seat_list) : 
	   try:
	      from_seat = WebDriverWait(web, 5).until(EC.element_to_be_clickable((By.ID, order_seat_from)))
	      from_seat.click()
	      j = 99  ## got seat 
	      logger_num1 = logging.getLogger(num)
	      logger_num1.info("choice seat_from num is sucesses")
	      time.sleep(random.randrange(2, 5, 1))
	   except:
	      if j <99 :
	         j=j+1
	
  #print('num_j:',j)
  ## seat is full
  elif j == len(seat_list) : 
     break
 
  if k < len(seat_list) :
	   try:
	      return_seat = WebDriverWait(web, 5).until(EC.element_to_be_clickable((By.ID, order_seat_return)))
	      return_seat.click()
	      k = 99
	      logger_num2 = logging.getLogger(num)	
	      logger_num2.info("choice return_seat num is sucesses")
	      time.sleep(random.randrange(2, 5, 1))
	   except:
	      if k < 99 :
	         k=k+1
	
  elif k == len(seat_list) :
       break
  ##  choice seat is all done
  if j == 99 and k == 99:
    break

## logging seat failed 
if j == len(seat_list) and k == 99 :
    logging.info("choice seat_from is failed")

elif j == 99 and k == len(seat_list):
    logging.info("choice return_seat from is failed")

	
if j == 99 and k == 99: # choice sucesses 
        ##radio
        ###choice ticket amount:1
        try:	
        	web.find_element_by_id('ctl00_ContentPlaceHolder1_rdoATot_Count_0').click()
        	time.sleep(random.randrange(1, 5, 1))
        	logging.info("setting ticket_1 amount is sucesses")
        	## choice return ticket  count
        except :
        	logging.info("setting ticket_1 amount is failed")
        	#web.quit()
        	#display.stop()
        	
        
        try:
        	web.find_element_by_id('ctl00_ContentPlaceHolder1_rdoBTot_Count_0').click()
        	time.sleep(random.randrange(1, 5, 1))
        	logging.info("setting ticket_2 amount is sucesses")
        except :
        	logging.info("setting ticket_2 amount is failed")
        	#web.quit()
        	#display.stop()
        
         
        ### finshed book bus ticket
        try :
        	step4_click = web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep4_OK")
        	step4_click.click()
        	time.sleep(random.randrange(3, 5, 1))
        	#print('step4_click book ticket is success')
        	logging.info("step4_click book  ticket  is success")
        except :
        	logging.info("step4_click book  ticket is failed")
        	#web.quit()
        	#display.stop()
        
        
        ### step 5 payment keyin ticket num
        
        j = 0
        k = 0
        
        for num in range(len(ticket_num)): 
        
        	from_ticket ,return_ticket = random_ticket()
        
        	time.sleep(random.randrange(3, 5, 1))
        
        	## payment key ticket no1 
        	if j < len(ticket_num) :
        	   try:
        	       web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCoupon_TicketNo1").send_keys(from_ticket)
        	       logger1 = logging.getLogger(from_ticket)	       
        	       logger1.info("step5_1 TicketNo1 keys in is sucesses")
        	       time.sleep(random.randrange(3, 5, 1))
        	       j = 99
        
        	   except:
                       if j < 99 :
                        j = j+1
        	   #print('from_ticket:',from_ticket)	
        	   #print('payment_j:',j)
        	elif j == len(ticket_num) :
        	       #web.quit()
        	       #display.stop()
        	       logging.info("step5_1 TicketNo1 from_ticket is faild")
        
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
        
        	   #print('return_ticket:',return_ticket)
        	   #print('payment_k:',k)
        	elif k == len(ticket_num) :
        	       #web.quit()
        	       #display.stop()
        	       logging.info("step5_2 TicketNo5 return_ticket is faild")
        	
        	if j == 99 and k == 99 :
        	   break
        
         
        ## payment button 
        try :
             pay_click = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnPayByPrepaidTickets")))
             pay_click.click() 
             logging.info("step5_click payment is success")
             logger3 = logging.getLogger(day_from)
             logger4 = logging.getLogger(day_return)
             logger3.info("day_from booking is success")
             logger4.info("day_return booking is success")
            	
        except:
               #web.quit()
               #display.stop()
               logging.info("step5_click payment is faild")



web.quit()
display.stop()


body = ''
try:
    with open('kingbus.log') as fp:
      data = fp.readlines()
      for i in data[-22:]:
          body  = body + i

finally:
    fp.close()

send_mail.send_email('kingbus auto booking ',body)
