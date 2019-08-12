from datetime import datetime
import configparser
import sqlite3
import vk_api
import time
import os

import db_tools as db

UPDATE_TIME = 60 # In seconds

config = configparser.ConfigParser()
config.read("./config/config.conf")


vk_session = vk_api.VkApi(config['Auth']['vk_login'], config['Auth']['vk_password'])
vk_session.auth()
vk = vk_session.get_api()

conn = db.CreateDB('init.sql')

def GetUnixTimestamp():
    return datetime.now().timestamp()


def get_friends():
    result = {}    
    friends = vk.friends.get(fields=['sex, nickname'])['items']
    timestamp = GetUnixTimestamp()

    for user in friends:
        cur = db.GetLastState(conn, int(user['id']))
        data = cur.fetchone()

        if data != None and data[2] != None:
            if int(data[2]) == int(user['online']):
                continue
            
        result[ user['id'] ] = { 'id': user['id'], 'online': user['online'], 'timestamp': timestamp };


    return result

i = 0
while (True):
    i = i + 1
    print( 'Check' + str( i ) )
    db.InsertMetrics(conn, get_friends())
    time.sleep( UPDATE_TIME )
            