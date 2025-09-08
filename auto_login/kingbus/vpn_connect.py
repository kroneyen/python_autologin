#! /usr/bin/env python3.7
# -*- coding: utf-8 -*-

import redis
import pexpect
from pexpect import popen_spawn
import time
import random



pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.StrictRedis(connection_pool=pool)


def get_redis_data_vpn(_key,_type,_field_1,_field_2):

    if _type == "lrange" :
       _list = r.lrange(_key,_field_1,_field_2)

    elif _type == "hget" :
       _list = r.hget(_key,_field_1)

    elif _type == "hgetall" :
       _list = r.hgetall(_key)


    return _list




def vpn_connect(opt):

    ### get vpn data 
    data_vpn = get_redis_data_vpn('vpn_key','hgetall','NaN','NaN')
    user = data_vpn.get('user')
    pwd = data_vpn.get('pwd')
   
    vpn_domain_list = get_redis_data_vpn('no_ip_domain_list','lrange',-1 ,-1)
    vpn_domain = vpn_domain_list[0].replace('.','_')


    if opt == 'conn' :

      commands = "openvpn3 session-start --config " + vpn_domain

      commands_list = commands.split(" ")

      session = pexpect.popen_spawn.PopenSpawn(commands)
      session.expect("Auth User name: ")
      session.sendline(user)
      time.sleep(random.randrange(1, 3, 1))
      session.expect("Auth Password: ")
      session.sendline(pwd)
      print(vpn_domain + ' VPN connect successes')


    elif opt == 'dis'  :

      commands = "openvpn3 session-manage --config " + vpn_domain + " --disconnect"
      commands_list = commands.split(" ")
      session = pexpect.popen_spawn.PopenSpawn(commands)
      print(vpn_domain + ' VPN disconnect successes')


if __name__ == '__main__':

   vpn_connect('conn')

   time.sleep(random.randrange(5, 10, 1))

   vpn_connect('dis')
