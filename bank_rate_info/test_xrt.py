#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import re  
import logging
import calendar
import datetime

url ='http://rate.bot.com.tw/xrt/history/USD'
s = requests.session()
req = s.get(url,timeout=3)

