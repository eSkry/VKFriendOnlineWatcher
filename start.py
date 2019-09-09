from datetime import datetime
import configparser
import sqlite3
import vk_api
import time
import os

import db_tools as db
import pushgateway_tools as pgt

UPDATE_TIME = 60 # In seconds

config = configparser.ConfigParser()
config.read("./config/config.conf")

conn = db.CreateDB('init.sql')

def GetUnixTimestamp():
    return datetime.now().timestamp()


def get_friends(vk):
    result = {}    
    friends = vk.friends.get(fields=['sex, nickname'])['items']
    timestamp = GetUnixTimestamp()

    pushgateway_str = ""

    for user in friends:
        cur = db.GetLastState(conn, int(user['id']))
        data = cur.fetchone()

        if data != None and data[2] != None:
            full_name = str(user['first_name']) + ' ' + str(user['last_name'])
            pushgateway_str += 'friends_online_stats{user="' +  str(user['id']) + '", full_name="' + full_name + '"} ' + str(user['online']) + '\n'
            if int(data[2]) == int(user['online']):
                continue
        
        result[ user['id'] ] = { 'id': user['id'], 'online': user['online'], 'timestamp': timestamp };
    
    pgt.SendMetrics(pushgateway_str)

    return result


while (True):
    try:
        print('Working')
        vk_session = vk_api.VkApi(config['Auth']['vk_login'], config['Auth']['vk_password'])
        vk_session.auth()
        vk = vk_session.get_api()
        while (True):
            db.InsertMetrics(conn, get_friends(vk))
            time.sleep( UPDATE_TIME )
    except ConnectionError:
        print('Connection to VK error')
    except:
        print('Stop working')
        print('Error in main stream, continue work....')
    finally:
        time.sleep( 1 )
