#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pyvirtualdisplay import Display #nodisplay on chrome
from selenium.common.exceptions import NoSuchElementException ## show error msg
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import logging
import send_mail

#logging.basicConfig(level=logging.INFO,
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='no_ip.log',
                    filemode='a')

logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

link_url = 'https://www.noip.com/login'
hostname_url = 'https://my.noip.com/#!/dynamic-dns'


## Usage Virtual Dispaly
display = Display(visible=0, size=(800, 600))
display.start()
web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path
##web = webdriver.Chrome()
web.get(link_url)

myusername='XXXXXXXX'
mypassword ='XXXXXXXX'

time.sleep(random.randrange(1, 5, 1))


### login for from 
loging_from = web.find_element_by_id('clogs')

loging_from.find_element_by_name("username").send_keys(myusername)
time.sleep(random.randrange(1, 5, 1))
loging_from.find_element_by_name("password").send_keys(mypassword)
time.sleep(random.randrange(1, 5, 1))
loging_from.find_element_by_name("Login").submit()

time.sleep(random.randrange(1, 5, 1))

#### web get expire hostname 
web.get(hostname_url)

time.sleep(random.randrange(1, 5, 1))

logging.info("loging account is successed!!")




#### btn_confirm
j = 1 


for i in range(3)  : ## 3 domain hostname
 try :
      btn_confirm = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(.,'Confirm')]")))
      btn_confirm.click()
      logging.info("domain confirm is successed!!")
      j =99


 except : 
          try :
              if j == 99 and i <3 :
               logging.info("domain confirm is all down !!")
              else :
               logging.info("domain confirm is all pass !!")
          finally :          
             break

 time.sleep(random.randrange(1, 5, 1))

### loop down waiting 
time.sleep(random.randrange(1, 3, 1))
web.quit()
display.stop()


if j ==99 :

     ### read for log last 5 line of mail body
     body = ''
     try:
             with open('no_ip.log') as fp:
              data = fp.readlines()
              for i in data[-5:]:
               body  = body + i

     finally:
         fp.close()


     send_mail.send_email('no_ip auto confirm loging',body)

