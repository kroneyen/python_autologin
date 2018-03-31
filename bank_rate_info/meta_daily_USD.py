#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import re  
import logging
import calendar
import datetime

headers = {
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
         'Accept-Encoding': 'gzip, deflate, br',
         'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
         'Cache-Control': 'max-age=0',
         'Connection': 'keep-alive',
         'User-Agent':'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1' 

}
""" 
        <option value="01">美金[USD]</option>
	<option value="03">港幣[HKD]</option>
	<option value="04">英鎊[GBP]</option>
	<option value="05">澳幣[AUD]</option>
	<option value="06">新加坡幣[SGD]</option>
	<option value="07">瑞士法郎[CHF]</option>
	<option value="08">日圓[JPY]</option>
	<option value="09">加拿大幣[CAD]</option>
	<option value="12">瑞典幣[SEK]</option>
	<option value="13">韓幣[KRW]</option>
	<option value="14">馬來幣[MYR]</option>
	<option value="15">印尼幣[IDR]</option>
	<option value="17">泰幣[THB]</option>
	<option value="21">菲律賓幣[PHP]</option>
	<option value="24">紐西蘭幣[NZD]</option>
	<option value="27">南非幣[ZAR]</option>
	<option value="28">澳門幣[MOP]</option>
	<option value="37">歐元[EUR]</option>
	<option value="38">越南幣[VND]</option>
	<option value="39">人民幣[CNY]</option>
"""


## datetime prepare

today = datetime.date.today()
###%s/%s/%s
str_today = datetime.date.today().strftime("%Y/%m/%d")

date_1 = today.strftime("%Y/%m/")
##first
date_first = date_1+'01'
date_last = date_1 + str(calendar.monthrange(today.year,today.month)[1])



url ='https://ebank.megabank.com.tw/global2/rs/rs03/PRS3000.faces?taskID=PRS300'
url_1 = 'https://ebank.megabank.com.tw' 
s = requests.session()
req = s.get(url,timeout=3)

## get ptoken web_page
soup=BeautifulSoup(req.text, "html.parser")
ptoken = soup.find('form')
ptoken_url = url_1+ptoken.get('action')
#print(url_1+ptoken.get('action'))

## get javax.faces.ViewState
viewstate = soup.find('input',id='javax.faces.ViewState').get('value')
#print(viewstate)

##USD
payload = {
        'main': 'main',
        'main:currency': '01',
        'typeGrp': 'DCR',
        'main:startDate': str_today,
        'main:endDate': str_today,
        'main:downloadType': 'TEXT',
        'autoDisabled:main:j_id27': 'AutoDisabled:Clicked',
        'submitTrigger': '',
        'autoDisabled:main:fileDownload': '',
        'autoDisabled:main:j_id28': '',
        'main:hidstartdate': date_first,
        'main:hidenddate': date_last,
        'javax.faces.ViewState': viewstate

}


## loging ptoken
trlist=[]
tdlist=[]
head_top=[]

req_ptoken=s.post(ptoken_url,data = payload,headers = headers,timeout =3)
soup_ptoken = BeautifulSoup(req_ptoken.text, "html.parser")
#print(soup_ptoken)

### get table_head_top 
table_head_top = soup_ptoken.find('table',class_='table_head_top')
for thead in table_head_top.find_all('thead'):
 for td in thead.find_all('td'):
  if td.text != '\u3000\u3000\u3000\u3000\u3000':
   head_top.append(td.text) 
#print(head_top)

### get tbody content
for tbody  in soup_ptoken.find_all('tbody'):
  for tr in tbody.find_all('tr'): ## get tr content
    trlist.append(tr.text)
    for td in tr.find_all('td'):  ## get td content
     if td.text != '\u3000': 
      tdlist.append(td.text)

#print(len(trlist),len(tdlist))
## get top data 
for i in range(0,6,2):
 print (tdlist[i],tdlist[i+1])

## get data 
for i in range(6,len(tdlist)):
 j = i % len(head_top) -1
 if j == 0 :
  print("") 
 print (head_top[j],tdlist[i])

s.close()
s.cookies.clear()


