# -*- coding: utf-8 -*-


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.common.exceptions import NoSuchElementException  ## 拋出異常訊息
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


myusername ="XXXXXX" 
myphone ="XXXXXXX"

#url="http://www.p2p101.com/"
#url_2="http://www.p2p101.com/home.php?mod=task&amp;do=apply&amp;id=3" ##user_task_page
order_check="https://order.kingbus.com.tw/ORD/ORD_M_1540_ViewOrder.aspx"


web = webdriver.Chrome()

web.get(order_check)

web.find_element_by_id("ctl00_ContentPlaceHolder1_txtCustomer_ID").send_keys(myusername)
web.find_element_by_id("ctl00_ContentPlaceHolder1_txtPhone").send_keys(mypassword)


time.sleep(1)
web.find_element_by_id("ctl00_ContentPlaceHolder1_btnQuery").submit() #點擊登入

#web.find_element_by_xpath("//button[contains(@class, 'pn vm')]").submit() #點擊登入
print("login botton is success")

time.sleep(1)


#web.get(url_2)
"""
print("login task page is success")

time.sleep(1)


##領取紅包
try:
    link = WebDriverWait(web, 10).until(EC.element_to_be_clickable((By.XPATH, "//img[@alt='apply']")))
    link.click()
    print('link is success!!')



except:
       print('link is not exist!!')
    

"""
web.quit()


