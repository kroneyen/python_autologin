# -*- coding: utf-8 -*-

#from __future__ import print_function
#from apiclient.discovery import build
#from httplib2 import Http
#from oauth2client import file, client, tools
#import urllib.request

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException  ## 拋出異常訊息
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random


#web = webdriver.Chrome() ## for cron path
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path
#link_url = 'https://www.noip.com/confirm-host?n=Dk2kVXu1ZO6jHEa5rvA'
link_url = 'https://www.noip.com/login'
hostname_url = 'https://my.noip.com/#!/dynamic-dns'

web = webdriver.Chrome()
web.get(link_url)

myusername='XXXXXXXXX'
mypassword ='XXXXXXXXX'

time.sleep(random.randrange(1, 5, 1))


### login for from 
loging_from = web.find_element_by_id('clogs')

loging_from.find_element_by_name("username").send_keys(myusername)
time.sleep(random.randrange(1, 2, 1))
loging_from.find_element_by_name("password").send_keys(mypassword)
time.sleep(random.randrange(1, 2, 1))
loging_from.find_element_by_name("Login").submit()

time.sleep(random.randrange(1, 5, 1))

#### get expire hostname 
btn_confirm = []
web.get(hostname_url)

time.sleep(random.randrange(1, 5, 1))


#### btn_confirm_1
try :
     btn_confirm = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(.,'Confirm')]")))
     btn_confirm.click()     
     print('btn_confirm is sucesses:',)


except : 
        pass	    
        print("btn_confirm_1 is pass")

time.sleep(random.randrange(1, 5, 1))



web.quit()
