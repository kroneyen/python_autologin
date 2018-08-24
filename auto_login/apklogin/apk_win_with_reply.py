from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
#from pyvirtualdisplay import Display #nodisplay on chrome
from selenium.common.exceptions import NoSuchElementException ## show error msg
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
#import send_mail
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.action_chains import ActionChains



myusername_list =["XXXXX"]
mypassword_list =["XXXX"]
#uid_list = ["XXXXXX"]   


url="https://apk.tw/forum.php"
url2="https://apk.tw/home.php?mod=task&do=view&id=7" ##user_task_page of week
bt_hd_url="https://apk.tw/forum-883-1.html" ##BT HD page
#bt_hd_url="https://apk.tw/forum-883-1.html" ##BT HD page
#https://apk.tw/thread-884337-1-1.html
url_credit = 'https://apk.tw/home.php?mod=spacecp&ac=credit'
reply_history_p1 ='https://apk.tw/home.php?mod=space&'
reply_history_p2 ='&do=thread&view=me&type=reply&from=space'


#logger = logging.getLogger(bt_hd_url)
#logger.info("BT HD page !!")

### Usage Virtual Dispaly


myusername='XXXXX'
mypassword ='XXXX'       
#myreply_history_url = reply_history_p1+ uid_list[num] + reply_history_p2
#log_file = 'myreply_history_'+myusername+'.log'    

web = webdriver.Chrome() ## for cron path  
#web = webdriver.Chrome('/usr/local/bin/chromedriver') ## for cron path      
web.get(url)
time.sleep(random.randrange(1, 10, 1))
#soup = BeautifulSoup(web.page_source , "html.parser")
#print(soup.prettify())
#loginForm  = web.find_element_by_css_selector(".mousebox")
loginForm  = web.find_element_by_class_name("mousebox")
fromname   = web.find_element_by_css_selector(".mousebox  #ls_username")
frompwd   = web.find_element_by_css_selector(".mousebox #ls_password")
click_btn =web.find_element_by_xpath("//*[@id='lsform']/div/div/button/em")
#click_btn =web.find_element_by_xpath("//button[contains(@class, 'pn vm')]")

ActionChains(web).move_to_element(loginForm).send_keys_to_element(fromname,myusername).send_keys_to_element(frompwd,mypassword).click(click_btn).perform()
time.sleep(random.randrange(10, 20, 15))



#print(web.current_url)
#print(ls_username.text , ls_password.text)
web.quit()


