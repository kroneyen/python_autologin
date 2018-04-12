# -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from selenium.common.exceptions import NoSuchElementException  ## 拋出異常訊息
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import random
from selenium.webdriver.support.ui import Select


myusername =["XXXXXXXXX"] 
mypassword =["XXXXXXXXX"]

s_start_id ='A03' ##<option value="A03">台北轉運</option>
s_end_id ='H26' ##<option value="H26">朝　　馬　</option>
day_from = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days = 4),'%Y/%m/%d')
day_return = datetime.datetime.strftime(datetime.date.today() + datetime.timedelta(days = 7),'%Y/%m/%d')
time_from_h ='18'
time_from_m ='50'
time_return_h ='06'
time_return_m ='00'

ticket_num = ['XXXXXXXXX','XXXXXXXXX','XXXXXXXXX',
              'XXXXXXXXX','XXXXXXXXX','XXXXXXXXX',
              'XXXXXXXXX','XXXXXXXXX']

def random_ticket():
  i = random.randrange(0,len(ticket_num),1)
  ticket_1 = ticket_num[i]
  if i == (len(ticket_num)-1) :
    ticket_2 = ticket_num[0]
  else :
    ticket_2 = ticket_num[i+1]

  return ticket_1 , ticket_2


order_url="https://order.kingbus.com.tw/ORD/ORD_M_1520_OrderGoBack.aspx"


web = webdriver.Chrome()

web.get(order_url)

web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCustomer_ID").send_keys(myusername)
web.find_element_by_id("ctl00_ContentPlaceHolder1_txtPhone").send_keys(mypassword)
time.sleep(random.randrange(1, 5, 1))
step1_click = web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep1_OK")
step1_click.click()

time.sleep(random.randrange(1, 5, 1))
print('step1_next_click is success')

### step 2
### choice station  from 台北轉運 to 朝　　馬
Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlStation_ID_From")).select_by_value(s_start_id)

time.sleep(random.randrange(1, 5, 1))
Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlStation_ID_To")).select_by_value(s_end_id)

time.sleep(random.randrange(1, 5, 1))

### choice station  from date , rutern date
web.find_element_by_id("ctl00_ContentPlaceHolder1_txtAOut_Dt").send_keys(day_from)

time.sleep(random.randrange(1, 5, 1))

web.find_element_by_id("ctl00_ContentPlaceHolder1_txtBOut_Dt").send_keys(day_return)

time.sleep(random.randrange(1, 5, 1))


### check from  time

Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlAHour")).select_by_value(time_from_h)
time.sleep(random.randrange(1, 5, 1))
Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlAMinute")).select_by_value(time_from_m)
time.sleep(random.randrange(1, 5, 1))

Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlBHour")).select_by_value(time_return_h)
time.sleep(random.randrange(1, 5, 1))
Select(web.find_element_by_id("ctl00_ContentPlaceHolder1_ddlBMinute")).select_by_value(time_return_m)
time.sleep(random.randrange(1, 5, 1))


step2_click = web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep2_OK")
step2_click.click()

time.sleep(random.randrange(1, 10, 1))
print('step2_next_click is success')

### step 3

## choice from schdule
try:
    #from_botton = web.find_element_by_xpath("//*[@id='ctl00_ContentPlaceHolder1_grdAList']/tbody/tr[3]/td[2]/input")
    from_botton = WebDriverWait(web, 15).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_grdAList']/tbody/tr[3]/td[2]/input")))
    from_botton.click() 
    time.sleep(random.randrange(1, 5, 1))
    print('step3_click_1 is success')

except:
    print('step3_click_1 is faild')
    
## choice return schdule

try:          
    return_botton = WebDriverWait(web, 15).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='ctl00_ContentPlaceHolder1_grdBList']/tbody/tr[3]/td[2]/input")))
    return_botton.click() 
    time.sleep(random.randrange(1, 5, 1))
    print('step3_click_2 is success')


except:
    print('step3_click_2 is faild')



step2_click = web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep3_OK")
step2_click.click()
   
time.sleep(random.randrange(1, 5, 1))
print('step3_next_click is success')    

### step 4

### step 4

###choice  seat

def change_seat(num):
  seat_from='ctl00_ContentPlaceHolder1_ckb1A'  ## from_seat 
  seat_return='ctl00_ContentPlaceHolder1_ckb1B' ## return_seat 

  if num <= 10 :
   order_seat_from = seat_from+'0'+ str(num)
   order_seat_return = seat_return +'0' + str(num)
  else :
   order_seat_from = seat_from + str(num)
   order_seat_return = seat_return + str(num)
 
  return order_seat_from,order_seat_return

### for loop choice seat
j=1
k=1

for num in range(8,5,-1):  ##seat num from 8,7,6
 order_seat_from,order_seat_return = change_seat(num)

 if j < 4 : 
   try:
       from_seat = WebDriverWait(web, 3).until(EC.element_to_be_clickable((By.ID, order_seat_from)))
       from_seat.click()
       j = 99  ## got seat 
       print("seat_from is sucesses")
       time.sleep(random.randrange(1, 2, 1))
   except:
       j=j+1

   #print('num_j:',j)
       
 elif j == 4 :  ## full seat
      web.quit()
      
      print("seat_from is failed")
      
 elif k < 4 :
   try:
       return_seat = WebDriverWait(web, 3).until(EC.element_to_be_clickable((By.ID, order_seat_return)))
       return_seat.click()
       k = 99
       print("return_seat is sucesses")
       time.sleep(random.randrange(1, 2, 1))
   except:
       k=k+1
       
   #print('num_k:',k)

 elif k == 4 :
      web.quit()
      
      print("return_seat is failed")
   
 
##radio
###choice from ticket count 
web.find_element_by_id('ctl00_ContentPlaceHolder1_rdoATot_Count_0').click()
time.sleep(random.randrange(1, 5, 1))
## choice return ticket  count
web.find_element_by_id('ctl00_ContentPlaceHolder1_rdoBTot_Count_0').click()
time.sleep(random.randrange(1, 5, 1))


step4_click = web.find_element_by_id("ctl00_ContentPlaceHolder1_btnStep4_OK")
step4_click.click()

time.sleep(random.randrange(1, 10, 1))
print('step4_click is success')


### step 5 payment keyin ticket num

from_ticket ,return_ticket = random_ticket()

time.sleep(random.randrange(1, 10, 1))

## payment key ticket no1 
try:
    web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCoupon_TicketNo1").send_keys(from_ticket)
    print("TicketNo1 keys in is sucesses")
    time.sleep(random.randrange(1, 10, 1))

except:
      web.quit()
      print("from_ticket is faild")


## payment key ticket no5 
try:
    web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCoupon_TicketNo5").send_keys(return_ticket)
    print("TicketNo5 keys in is sucesses")
    time.sleep(random.randrange(1, 10, 1))

except:
      web.quit()
      print("return_ticket is faild")



## payment button 
try :
     pay_click = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnPayByPrepaidTickets")))
     pay_click.click() 
     print("step5_click  is success")

except:
       web.quit()
       print("step5_click  is faild")



print(day_from "booking is success")
print(day_return "booking is success")


web.quit()








