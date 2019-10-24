from datetime import datetime
import configparser
import sqlite3
import vk_api
import signal
import time
import sys
import os

from modules import db_sqlite as db
from modules import pushgateway_tools as pgt
from modules import fs_tools

UPDATE_TIME = 60 # In seconds

CONFIG_PATH = fs_tools.GetConfigPath()
config = configparser.ConfigParser()
config.read(CONFIG_PATH)

PUSHGATWAY_SEND = config['Prometheus']['active'].lower() == "true"

VK_USER_IDS = []
DOP_USER_IDS = []

def GetUnixTimestamp():
    return datetime.now().timestamp()


def update_metrics(vk, conn):
    friends = vk.friends.get(fields=['online', 'last_seen'])['items']
    dop_users = vk.users.get(user_ids=DOP_USER_IDS, fields=['online', 'last_seen'])
    user_status_list = friends + dop_users

    timestamp = GetUnixTimestamp()

    pgt_sender = pgt.PushgatewaySender(config['Prometheus']['host'])

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
                tags = { 'user': user_id, 'full_name': full_name, 'platform': user_last_seen }
                pgt_sender.AddToPool( pgt_sender.GetMetricsStr('friends_online_stats', tags, str(user_online)) )
            if int(state) == user_online:
                continue

        if user_online == 0:
            db.InsertOffline2(conn, user_id, timestamp, user_last_seen, False)
        elif user_online == 1:
            db.InsertOnline2(conn, user_id, timestamp, False)

    conn.commit()
    
    if PUSHGATWAY_SEND:
        try:
            pgt_sender.SendFromPool()
        except Exception as e:
            print('Pushgateway send error')
            print(e)
        finally:
            pass


KILL_APP = False

def __handle_exit(sig, frame):
    KILL_APP = True
    print('\nEXITING')
    time.sleep(2)
    sys.exit(0)

signal.signal(signal.SIGINT, __handle_exit)
signal.signal(signal.SIGTERM, __handle_exit)

if CONFIG_PATH == None:
    print('Config is not exists! Please create config cin ./config/config.conf')
    sys.exit(0)

print('Using config file: {}'.format(CONFIG_PATH))
conn = db.CreateDB('./sql/init.sql')

try:
    vk_session = vk_api.VkApi(config['Auth']['vk_login'], config['Auth']['vk_password'])
    vk_session.auth()
    vk = vk_session.get_api()

    if config.has_section('Users'):
        DOP_USER_IDS = fs_tools.GetIdList(config['Users']['file'])

    while not KILL_APP:
        update_metrics(vk, conn)
        time.sleep(UPDATE_TIME)

except Exception as e:
    print(e)
finally:
    conn.close()
    KILL_APP = True

print('Stop working')