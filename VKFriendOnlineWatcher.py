from datetime import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
import vk_api
import signal
import time
import sys
import os

from modules import db_sqlite as db
from modules import pushgateway_tools as pgt
from modules import fs_tools
import confloader

UPDATE_TIME = 60 # In seconds

VK_USER_IDS = []

class Main(object):
    def __init__(self):
        self.CONFIG = confloader.VKFOConfig()
        self.vk_session = vk_api.VkApi(login=self.CONFIG.VK_LOGIN, password=self.CONFIG.VK_PASSWORD)
        self.vk_session.auth()
        self.vkapi = self.vk_session.get_api()
        self.longpool = VkLongPoll(self.vk_session)
        self.VK_USER_IDS = []
        self.DOP_USER_IDS = []

        if self.CONFIG.PROMETHEUS_SEND:
            self.pgt_sender = pgt.PushgatewaySender(self.CONFIG.PROMETHEUS_HOST)

        if self.CONFIG.HAS_UPSER_FILE:
            self.DOP_USER_IDS = fs_tools.GetIdList(self.CONFIG.USERS_FILE)

        signal.signal(signal.SIGINT, self._handleExit)
        signal.signal(signal.SIGTERM, self._handleExit)

        self.Loop()

    def Loop(self):
        for event in self.longpool.listen():
            if event.type == VkEventType.USER_ONLINE:
                pass
            if event.type == VkEventType.USER_OFFLINE:
                pass
            

    def GetUnixTimestamp(self):
        return datetime.now().timestamp()

    def _handleExit(self, sig, frame):


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

        full_name = '{} {}'.format(user['first_name'], user['last_name'])
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

if CONFIG_PATH == None:
    print('Config is not exists! Please create config cin ./config/config.conf')
    sys.exit(0)

print('Using config file: {}'.format(CONFIG_PATH))
conn = db.CreateDB('./sql/init.sql')

while not KILL_APP:
    update_metrics(vk, conn)
    time.sleep(UPDATE_TIME)

print('Stop working')