#! /usr/bin/env python3.6
# -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import datetime
from pyvirtualdisplay import Display #nodisplay on chrome
from selenium.common.exceptions import NoSuchElementException ## show error msg
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import random
import logging
import send_mail
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.action_chains import ActionChains

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='no_ip.log',
                    filemode='a')

logging.info(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))

link_url = 'https://www.noip.com/login'
hostname_url = 'https://my.noip.com/dynamic-dns'
#hostname_url = 'https://www.noip.com/members/dns/'

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
web = webdriver.Chrome(options=options)





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
            elif section_list =='domain':
               domain_list = ast.literal_eval(config.get(section_list,key))
              
    return myusername_list , mypassword_list ,domain_list ## return for drama

def get_redis_data():
    import redis
    pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
    r = redis.StrictRedis(connection_pool=pool)

    myusername_list = r.lrange('no_ip_myusername_list','0','-1')
    mypassword_list = r.lrange('no_ip_mypassword_list','0','-1')
    domain_list = r.lrange('no_ip_domain_list','0','-1')

    return myusername_list , mypassword_list ,domain_list

def get_option_num(soup,tb_id,_domain) :
    table_id = soup.find('table',{'class':re.compile(tb_id)})  ## find table_id                                   
    _tr_class_list = []
    row_num =1
    ### find striped-row                                                                                                            
    for _t_striped in table_id.find_all('tr',{'class':re.compile('table-striped-row')}):
        _tr_class_list.append(_t_striped)

    ### find domain && Confirm botton index 
    for _tr_class in _tr_class_list:
      #_td = _tr_class.find('a', {'class': re.compile('text-info cursor-pointer')})
      _td = _tr_class.find('a', {'class': re.compile('link-info cursor-pointer')})
      if _td.string == _domain:
             break
      else :
          row_num = row_num + 1

    return row_num 



### word replace of '*'
def mark_word(word):
    str = ''
    for nw in range(len(word)) :
       if nw >0 and  nw < (len(word) -8) :
          str = str + '*'
       else :
          str = str + word[nw]

    return str



## get user & pwd 
myusername_list , mypassword_list , domain_list = get_redis_data() ## get loging user && pwd 

    
### login for from 
for num in range(len(myusername_list)):
    myusername=myusername_list[num]
    mypassword =mypassword_list[num]
    
    web.get(link_url) 
    time.sleep(random.randrange(3, 5, 1))
    
    ### find loging_from 
    loginForm = web.find_element_by_id('clogs')
    fromname =loginForm.find_element_by_name("username")
    frompwd = loginForm.find_element_by_name("password")
    click_btn = loginForm.find_element_by_id("clogs-captcha-button")
    time.sleep(random.randrange(5, 10, 1))    
    
    ActionChains(web).move_to_element(loginForm).send_keys_to_element(fromname, myusername).pause(random.randrange(1, 3, 1)).send_keys_to_element(frompwd, mypassword).pause(random.randrange(1, 3, 1)).pause(random.randrange(1, 3, 1)).click(click_btn).perform()
    time.sleep(random.randrange(5, 10, 1))
   
    #### web get expire hostname login
    web.get(hostname_url)
    time.sleep(random.randrange(5, 10, 1))
    logger = logging.getLogger(mark_word(myusername))
    logger.info("loging account hostname page is successed!!")
    
    soup = BeautifulSoup(web.page_source , "html.parser")
    pass_domain_list = []
    ### domain confirm botton check 
    for domain_idx in domain_list :
        condi = ''
        o_num  =get_option_num(soup,'table no-margin-bv table-stack',domain_idx)

        #### 20240201 structure location turning 
        condi= '//*[@id="host-panel"]/table/tbody/tr['+ str(o_num) +']/td[6]/button[contains(.,"Confirm")]'
        chk_down= '//*[@id="host-panel"]/table/tbody/tr['+ str(o_num) +']/td[6]/button[contains(.,"Modify")]'
        logger = logging.getLogger(mark_word(domain_idx))
        try :
             btn_confirm = WebDriverWait(web, 15).until(EC.element_to_be_clickable((By.XPATH,condi)))
             btn_confirm.click()
             time.sleep(random.randrange(5, 10, 1))
             try : ### After check Modify status is exiest
                  WebDriverWait(web, 15).until(EC.presence_of_element_located((By.XPATH,chk_down)))
                  logger.info("domain %s confirm is successed!!" % mark_word(domain_idx))

             except :
               logger.info("domain %s confirm is failed!!" % mark_word(domain_idx))
               pass_domain_list.append(domain_idx)

        except :
                WebDriverWait(web, 15).until(EC.presence_of_element_located((By.XPATH,chk_down)))
                logger.info("domain %s confirm is pass !!" % mark_word(domain_idx))
                pass_domain_list.append(mark_word(domain_idx))

        ### wait next domain btn check 
        logging.info("waiting for next  domain!!")
        logging.info(" ")
        time.sleep(random.randrange(1, 10, 1)) 
    ### domain all done && colse web 
    time.sleep(random.randrange(1, 10, 1))
    #web.quit()

    ### next trun user 
    if num < (len(myusername_list)-1):
       logging.info("waiting for next  user!!")
       time.sleep(random.randrange(60, 180, 10))
    else :
          break

time.sleep(random.randrange(1, 10, 1))

domain_status= 0

if len(pass_domain_list) == 0 :

   logging.info("user Confirm  done!!")
   domain_status =1

else : 
   logging.info("user all pass!!")




web.quit()

     ### read for log last 5 line of mail body
body = ''
log_date = datetime.date.today().strftime("%Y-%m-%d")
try:
    with open('no_ip.log') as fp:
      data = fp.readlines()
      for i in data[-100:]:
          if log_date in i:  ## read only  today log 
             body  = body + i

finally:
         fp.close()


## domain status chk for mail 

if domain_status == 1 :

   send_mail.send_email('no_ip auto confirm loging',body)

else : 

      if datetime.datetime.today().isoweekday() == 1 : 

         send_mail.send_email('no_ip auto confirm loging',body)



