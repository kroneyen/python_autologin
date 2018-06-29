#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import re  
import logging
import calendar
import datetime

url ='http://rate.bot.com.tw/xrt/quote/day/USD'
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
table_head_top = soup.find('table',class_='table table-striped table-bordered table-condensed table-hover toggle-circle')
for thead in table_head_top.find_all('thead'):
 for th in thead.find_all('th'):
  if th.text !='' and th.text not in head_top:
   head_top.append(th.text)

"""
print(head_top)
print("")
print(tdlist)
print("")
print(trlist)

#print(head_top)
for i in range(len(tdlist)):
#for i in reversed(range(len(tdlist))):
#for i in range(len(tdlist)-1,0,-1):
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

for i in reversed(range(len(trlist))):
 j = i % len(head_top)
 print(head_top[j:],trlist[i])
"""
for i in range(0,len(tdlist),6):
 j = i % len(head_top)
 if j== 0 and i ==0 :
  print('')
  print(head_top[j],'\u3000','\u3000','\u3000','\u3000','\u3000','\u3000','\u3000','\u3000',head_top[j+1],'\u3000',head_top[j+2],head_top[j+4],'\u3000',head_top[j+2],head_top[j+5],'\u3000',head_top[j+3],head_top[j+4],'\u3000',head_top[j+3],head_top[j+5])
 #else :
 #print('')
 #print(head_top)
 print(tdlist[i],'\u3000','\u3000',tdlist[i+1],'\u3000','\u3000','\u3000','\u3000',tdlist[i+2],'\u3000','\u3000','\u3000','\u3000',tdlist[i+3],'\u3000','\u3000','\u3000','\u3000',tdlist[i+4],'\u3000','\u3000','\u3000','\u3000',tdlist[i+5])


s.close()
s.cookies.clear()
