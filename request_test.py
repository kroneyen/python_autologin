#!/usr/bin/env python3.6

import requests
from bs4 import BeautifulSoup
import time
import re  


#myusername='pekrone'
#mypassword='zcGj4XcnH5Zw6%%h1?;Q'
login_url='https://www.backpackers.com.tw/forum/login.php'

payload = {
    	's':'',
	'securitytoken':'guest',
	'do':'login',
	'vb_login_md5password':'450016c47da4c490d317698d7349d334',
	'vb_login_md5password_utf':'450016c47da4c490d317698d7349d334',
	'vb_login_username':'pekrone',
	'vb_login_password':''
}


headers = {
'Cache-Control': 'max-age=0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
'Content-Length': '188',
'Content-Type': 'application/x-www-form-urlencoded',
'Referer': 'https://www.backpackers.com.tw/forum/',
'Origin': 'https://www.backpackers.com.tw',
'Upgrade-Insecure-Requests': '1',
'Host': 'www.backpackers.com.tw',
'Connection': 'keep-alive'
}

s = requests.session()

req = s.post(login_url,data = payload ,headers =headers,timeout=5)

soup = BeautifulSoup(req.text ,"html.parser")

#print(req.status_code)

if req.status_code == requests.codes.OK: 
  time.sleep(5)
  print('loging is sucesses!!! wait 5 sec')
  print(soup)
    
  for link in soup.find_all('a'):
              alink=link.get('href')
              print(alink)
  try:
     alink_post=s.post(alink,timeout=10)  ## jump_page
     time.sleep(5)
     ## jump_page
     if alink_post.status_code == requests.codes.OK:
       print('jump is sucesses !!')
       print(alink_post.text)
       bsObj = s.get('https://www.backpackers.com.tw/forum/member.php?u=364543',timeout=10)  ## login user_page
       ##user_page
       if bsObj.status_code == requests.codes.OK:
         print('loging user_page is sucesses!!')

         soup = BeautifulSoup(bsObj.text, "html.parser")
       
         for active in  soup.find_all('div',{'id':'last_online'}):
            print('user last loging :' ,active.get_text())

         ## for img alt
         for re in soup.find_all('img',src=re.compile('images')):
            print('img_tag :' ,re.get('alt'))

         for logout in soup.find_all('a',href=re.compile('logouthash'),attrs={'rel':'nofollow'},limit =1):
            logouthash_url=logout.get('href')
            print ('logout url is: ' , logout.get('href'))
              
         time.sleep(1)

         logout_hash=s.get(logouthash_url,timeout=10)

         if logout_hash.status_code == requests.codes.OK:
           print('logout is sucesses!!')
         else:
              print('logout is failed')
       ##user_page 
       else:
            print('user_page is failed')
  
     else:
            print('jump is failed')
  
  except:
         print("link is not exist!!!")
          
else:
     print('loging is failed')
	
	
time.sleep(5)
s.close()
s.cookies.clear()




"""
## loging user_page 

bsObj = s.get('https://www.backpackers.com.tw/forum/member.php?u=364543',timeout=10)


print(bsObj.status_code,'loging user_page is sucesses!!')

time.sleep(5)

###get element form user_page 
soup = BeautifulSoup(bsObj.text, "html.parser")


for active in  soup.find_all('div',{'id':'last_online'}):
        print('user last loging :' ,active.get_text())




time.sleep(1)
## for img alt




for re in soup.find_all('img',src=re.compile('images')):
        print('img_tag :' ,re.get('alt'))




##get person data all of the world mapping




### got logouthas key 


for logout in soup.find_all('a',href=re.compile('logouthash'),attrs={'rel':'nofollow'},limit =1):
	logouthash_url=logout.get('href')
	print ('logout url is: ' , logout.get('href'))


#logouthash_url=logout.get('href')


time.sleep(1)

logout_headers = {
'Referer':'https://www.backpackers.com.tw/forum/',
'Content-Type': 'application/x-www-form-urlencoded',
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
'Referer': 'https://www.backpackers.com.tw/forum/member.php?u=364543',
'Upgrade-Insecure-Requests': '1',
'Host': 'www.backpackers.com.tw',
'Connection': 'keep-alive'
}

###logout 
s.get(logouthash_url,headers =logout_headers,timeout=10)

time.sleep(5)

print(s.status_code,'logout is sucesses !!')


##clear cookies
s.cookies.clear()
print('clear cookies down')
"""
