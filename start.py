from datetime import datetime
import configparser
import sqlite3
import vk_api
import os


config = configparser.ConfigParser()
config.read("./config/config.conf")


vk_session = vk_api.VkApi(config['Auth']['vk_login'], config['Auth']['vk_password'])
vk_session.auth()
vk = vk_session.get_api()


def GetUnixTimestamp():
    return datetime.now().timestamp()


def get_friends():
    result = {}    
    friends = vk.friends.get(fields=['sex, nickname'])['items']

    for user in friends:
        result[ user['id'] ] = { 'first_name': user['first_name'], 'last_name': user['last_name']
                                , 'is_online': user['online'], 'timestamp': GetUnixTimestamp() };

    return result

print( get_friends() )
            