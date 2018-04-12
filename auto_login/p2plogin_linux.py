#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-

## chromedrive 2.32

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from pyvirtualdisplay import Display #nodisplay on chrome
from selenium.common.exceptions import NoSuchElementException ## show error msg
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='logging.log',
		    filemode='a')


logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

myusername_list =["XXXXXX","XXXXXX"] 
mypassword_list =["XXXXXX","XXXXXX"]


url="http://www.p2p101.com/"
url2="http://www.p2p101.com/home.php?mod=task&amp;do=apply&amp;id=3" ##user_task_page

## Usage Virtual Dispaly
display = Display(visible=0, size=(800, 600))
display.start()
#web = webdriver.Chrome()
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path

## login user page


for i in range(len(myusername_list)):
	myusername=myusername_list[i] 
	mypassword =mypassword_list[i]
	
	web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path	
	web.get(url)
	time.sleep(1)
	web.find_element_by_id("ls_username").send_keys(myusername)
	web.find_element_by_id("ls_password").send_keys(mypassword)
	web.find_element_by_xpath("//button[contains(@class, 'pn vm')]").submit() ## login

	#logging.info("login botton is success")

	time.sleep(random.randrange(1, 5, 1))

	## login user task
        
	web.get(url2)
	time.sleep(random.randrange(1, 5, 1))
	
        ## got redpackage 
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
	if i < (len(myusername_list)-1):	
	   logging.info("waiting for next  user!!")
	   time.sleep(random.randrange(60, 180, 10))
	else :
	   break
        	

logging.info("user all done!!")
display.stop()
