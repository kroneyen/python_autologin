#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import re  
import logging
import calendar
import datetime

"""
<option value="USD" selected>美金（USD）</option>
<option value="HKD">港幣（HKD）</option>
<option value="GBP">英鎊（GBP）</option>
<option value="AUD">澳幣（AUD）</option>
<option value="CAD">加拿大幣（CAD）</option>
<option value="SGD">新加坡幣（SGD）</option>
<option value="CHF">瑞士法郎（CHF）</option>
<option value="JPY">日圓（JPY）</option>
<option value="ZAR">南非幣（ZAR）</option>
<option value="SEK">瑞典幣（SEK）</option>
<option value="NZD">紐元（NZD）</option>
<option value="THB">泰幣（THB）</option>
<option value="PHP">菲國比索（PHP）</option>
<option value="IDR">印尼幣（IDR）</option>
<option value="EUR">歐元（EUR）</option>
<option value="KRW">韓元（KRW）</option>
<option value="VND">越南盾（VND）</option>
<option value="MYR">馬來幣（MYR）</option>
<option value="CNY">人民幣（CNY）</option>
"""


#url ='http://rate.bot.com.tw/xrt/history/USD'
url='http://rate.bot.com.tw/xrt/quote/2018-03/USD'
s = requests.session()
req = s.get(url,timeout=3)

trlist=[]
tdlist=[]
#head_top=['時間', '幣別', '現金買入', '現金賣出' , '即期買入', '即期賣出']
head_top = []

soup=BeautifulSoup(req.text, "html.parser")
for tbody  in soup.find_all('tbody'):
  for tr in tbody.find_all('tr'):
    trlist.append(tr.text)
    for td in tr.find_all('td'):
      tdlist.append(td.text)
"""
print(len(trlist),len(tdlist))
print('')
print(trlist)
print('')

print(tdlist)
print('')
"""
### get table_head_top
table_head_top = soup.find('table',class_='table table-striped table-bordered table-condensed table-hover')
for thead in table_head_top.find_all('thead'):
 for th in thead.find_all('th'):
  if th.text !='' and th.text not in head_top:
   head_top.append(th.text)
print(head_top)


for i in range(len(tdlist)):
  j = i % len(head_top)
  if j == 2 :
   print (head_top[j],head_top[j+2],tdlist[i]) 
  elif j== 3:
   print (head_top[j-1],head_top[j+2],tdlist[i])
  elif j== 4:
   print (head_top[j-1],head_top[j],tdlist[i])
  elif j == 5 : 
   print (head_top[j-2],head_top[j],tdlist[i])
  else  :
   if j ==0 :
    print('')
   print(head_top[j],tdlist[i])


s.close()
s.cookies.clear()
