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
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO,
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
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path
##web = webdriver.Chrome()
#web.get(link_url)

time.sleep(random.randrange(1, 5, 1))

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

    return myusername_list , mypassword_list  ## return for drama


## get user & pwd 
myusername_list , mypassword_list  = get_config() ## get loging user && pwd 

    
### login for from 
for num in range(len(myusername_list)):
    myusername=myusername_list[num]
    mypassword =mypassword_list[num]
    
    web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path
    ##web = webdriver.Chrome()
    web.get(link_url) 
    time.sleep(random.randrange(1, 5, 1))
    
    ### find loging_from 
    loging_from = web.find_element_by_id('clogs')
    loging_from.find_element_by_name("username").send_keys(myusername)
    time.sleep(random.randrange(1, 5, 1))
    loging_from.find_element_by_name("password").send_keys(mypassword)
    time.sleep(random.randrange(1, 5, 1))
    loging_from.find_element_by_name("Login").submit()
    time.sleep(random.randrange(1, 5, 1))
     
    logger = logging.getLogger(myusername)
    logger.info("login botton is success")
    time.sleep(random.randrange(1, 5, 1))

    #### web get expire hostname login
    web.get(hostname_url)
    time.sleep(random.randrange(2, 5, 1))
    logger = logging.getLogger(myusername)
    logger.info("loging account hostname page is successed!!")
    soup = BeautifulSoup(web.page_source , "html.parser")
    #host_tag = soup.find_all("a", class_="text-info cursor-pointer")
    host_tag_list=[]
    for host_tag in soup.find_all("a", class_="text-info cursor-pointer") :
        host_tag_list.append(host_tag.string)

   # print(host_tag_list) 
    #### btn_confirm
    j = 1 
    #for i in range(3)  : ## 3 domain hostname
    for i in range(len(host_tag_list))  : ## 3 domain hostname
       try :
            btn_confirm = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH,"//button[contains(.,'Confirm')]")))
            btn_confirm.click()
            logger = logging.getLogger(host_tag_list[i])
            logger.info("domain confirm is successed!!")
            j =99


       except : 
              try :
                  if j == 99 and i <len(host_tag_list) :
                     logger.info("domain confirm is all down !!")
                  else :
                     logger.info("domain confirm is all pass !!")
              finally :          
                  break
       ### wait next btn check 
       time.sleep(random.randrange(2, 5, 1))

    ### Waiting next trun user  
    if num < (len(myusername_list)-1):
       logging.info("waiting for next  user!!")
       time.sleep(random.randrange(60, 180, 10))
    else :
          break

web.quit()
display.stop()

if j ==99 :

     ### read for log last 5 line of mail body
     body = ''
     try:
             with open('no_ip.log') as fp:
              data = fp.readlines()
              for i in data[-10:]:
               body  = body + i

     finally:
         fp.close()


     send_mail.send_email('no_ip auto confirm loging',body)

