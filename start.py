from datetime import datetime
import configparser
import sqlite3
import vk_api
import time
import os

import db_tools as db
import pushgateway_tools as pgt
import fs_tools

UPDATE_TIME = 60 # In seconds

config = configparser.ConfigParser()
config.read("./config/config.conf")

PUSHGATWAY_SEND = config['Prometheus']['active'].lower() == "true"

VK_USER_IDS = []
DOP_USER_IDS = []

def GetUnixTimestamp():
    return datetime.now().timestamp()


def get_friends(vk, conn):
    friends = vk.friends.get(fields=['online', 'last_seen'])['items']
    dop_users = vk.users.get(user_ids=DOP_USER_IDS, fields=['online', 'last_seen'])
    user_status_list = friends + dop_users

    timestamp = GetUnixTimestamp()

    pushgateway_str = ""

    for user in user_status_list:
        user_id = int(user['id'])
        user_online = int(user['online'])
        user_last_seen = -1
        if 'last_seen' in user:
            user_last_seen = int(user['last_seen']['platform'])

        full_name = str(user['first_name']) + ' ' + str(user['last_name'])
        state = db.GetLastState2(conn, user_id)

        if not user_id in VK_USER_IDS:
            VK_USER_IDS.append(user_id)
            if not db.IsUserExists(conn, user_id):
                db.AddNewUser(conn, user_id, full_name, False)

        if state != None:
            if PUSHGATWAY_SEND:
                pushgateway_str += 'friends_online_stats{user="' +  str(user_id) + '", full_name="' + full_name + '"} ' + str(user_online) + '\n'
            if int(state) == user_online:
                continue

        if user_online == 0:
            db.InsertOffline2(conn, user_id, timestamp, user_last_seen, False)
        elif user_online == 1:
            db.InsertOnline2(conn, user_id, timestamp, False)

    conn.commit()
    
    if PUSHGATWAY_SEND:
        try:
            pgt.SendMetrics(pushgateway_str)
        except Exception as e:
            print('Pushgateway send error')
            print(e)
        finally:
            pass

while (True):
    try:
        print('Working')
        vk_session = vk_api.VkApi(config['Auth']['vk_login'], config['Auth']['vk_password'])
        vk_session.auth()
        vk = vk_session.get_api()
        conn = db.CreateDB('init.sql')

        DOP_USER_IDS = fs_tools.GetIdList(config['Users']['file'])

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
