#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pyvirtualdisplay import Display #nodisplay on chrome
from selenium.common.exceptions import NoSuchElementException  ## 拋出異常訊息
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='no_ip.log',
                    filemode='a')

logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

## Usage Virtual Dispaly
display = Display(visible=0, size=(800, 600))
display.start()
web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path
link_url = 'https://www.noip.com/login'
hostname_url = 'https://my.noip.com/#!/dynamic-dns'

web = webdriver.Chrome()
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


#### btn_confirm
i = 1 
j = 1 
for i in range(4)  : ## 3 domain hostname
 try :
      btn_confirm = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(.,'Confirm')]")))
      btn_confirm.click()
      #logger = logging.getLogger(myusername)     
      logging.info("domain confirm is successed!!")
      j =2


 except : 
         if j == 1 :
          logging.info("domain confirm is pass!!")
         break

 time.sleep(random.randrange(1, 5, 1))


web.quit()
display.stop()

if j ==2 :

     ### read for log last 4 line of mail body
     body = ''
     try:
             with open('no_ip.log') as fp:
              data = fp.readlines()
              for i in data[-4:]:
               body  = body + i

     finally:
         fp.close()


     send_mail.send_email('no_ip auto confirm loging',body)

