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

def GetUnixTimestamp():
    return datetime.now().timestamp()


def get_friends(vk, conn):
    friends = vk.friends.get(fields=['sex, nickname'])['items']
    timestamp = GetUnixTimestamp()

    pushgateway_str = ""

    for user in friends:
        cur = db.GetLastState2(conn, int(user['id']))
        state = cur.fetchone()

        if state != None:
            full_name = str(user['first_name']) + ' ' + str(user['last_name'])
            pushgateway_str += 'friends_online_stats{user="' +  str(user['id']) + '", full_name="' + full_name + '"} ' + str(user['online']) + '\n'
            if int(state) == int(user['online']):
                continue
        
        if int(user['online']) == 0:
            db.InsertOffline2(conn, user['id'], timestamp)
        else if int(user['online'] == 1):
            db.InsertOnline2(conn, user['id'], timestamp)
    
    pgt.SendMetrics(pushgateway_str)


while (True):
    try:
        print('Working')
        vk_session = vk_api.VkApi(config['Auth']['vk_login'], config['Auth']['vk_password'])
        vk_session.auth()
        vk = vk_session.get_api()
        conn = db.CreateDB('init.sql')

        while (True):
            get_friends(vk, conn)
            time.sleep( UPDATE_TIME )

    except vk_api.AuthError:
        print('VK Auth error')
    except vk_api.VkApiError:
        print('VK API error')
    except Exception as e:
        print('Error in main stream, continue work....')
        print(e)
        print('Stop working')
    finally:
        time.sleep( 1 )
