from datetime import datetime
import threading, time
from vk_api.longpoll import VkLongPoll, VkEventType, VkLongpollMode
import vk_api
import signal
import time
import sys
import os

from modules import db_sqlite as db
from modules import pushgateway_tools as pgt
from modules import fs_tools
import confloader


class Main(object):
    def __init__(self):
        self.CONFIG = confloader.VKFOConfig()
        self.vk_session = vk_api.VkApi(login=self.CONFIG.VK_LOGIN, password=self.CONFIG.VK_PASSWORD, token=self.CONFIG.VK_TOKEN)
        self.vk_session.auth(token_only=True)
        self.longpoll = VkLongPoll(self.vk_session, mode=VkLongpollMode.GET_EXTRA_ONLINE)
        self.vkapi = self.vk_session.get_api()
        self.VK_USER_IDS = []
        self.DOP_USER_IDS = []
        self.DB = db.CreateDB('./sql/init.sql')
        self.ceck_timer = threading.Timer(60, self._updateDopUsers)
        self.main_timer = threading.Timer(1, self._loop)
        self.is_running = False

        if self.CONFIG.PROMETHEUS_SEND:
            self.pgt_sender = pgt.PushgatewaySender(self.CONFIG.PROMETHEUS_HOST)

        if self.CONFIG.HAS_UPSER_FILE:
            self.DOP_USER_IDS = fs_tools.GetIdList(self.CONFIG.USERS_FILE)

        signal.signal(signal.SIGINT, self._handleExit)
        signal.signal(signal.SIGTERM, self._handleExit)
        
        self.ceck_timer.start()
        self.Loop()

    def Start(self):
        self.is_running = True
        self.ceck_timer.start()
        self.main_timer.start()

    def Stop(self):
        self.is_running = False

    def _loop(self):
        for event in self.longpoll.listen():
            if not self.is_running:
                break

            tags = { 'user': event.user_id, 'full_name': event.full_name, 'platform': event.last_seen }
            if event.type == VkEventType.USER_ONLINE:
                db.InsertOnline(self.DB, event.user_id, event.timestamp)
                self.pgt_sender.AddToPool(self.pgt_sender.GetMetricsStr('friends_online_stats', tags, '1'))
            elif event.type == VkEventType.USER_OFFLINE:
                db.InsertOffline(self.DB, event.user_id, event.timestamp, event.last_seen)
                self.pgt_sender.AddToPool(self.pgt_sender.GetMetricsStr('friends_online_stats', tags, '0'))
            
            if event.user_id not in self.VK_USER_IDS:
                self.VK_USER_IDS.append(event.user_id)
                db.AddNewUser(self.DB, event.user_id, event.full_name)

    def _updateDopUsers(self):
        if not self.is_running:
            return

        dop_users = self.vkapi.users.get(user_uds=self.DOP_USER_IDS, fields=['online', 'last_seen'])
        timestamp = self.GetUnixTimestamp()
        for user in dop_users:
            user_id = int(user['id'])
            full_name = '{} {}'.format(user['first_name'], user['last_name'])
            user_online = int(user['online'])
            user_last_seen = -1

            if 'last_seen' in user:
                user_last_seen = int(user['last_seen']['platform'])

            if not user_id in self.VK_USER_IDS:
                self.VK_USER_IDS.append(user_id)
                if not db.IsUserExists(self.DB, user_id):
                    db.AddNewUser(self.DB, user_id, full_name, False)

            state = db.GetLastState(self.DB, user_id)
            if state != None:
                if self.CONFIG.PROMETHEUS_SEND:
                    tags = { 'user': user_id, 'full_name': full_name, 'platform': user_last_seen }
                    self.pgt_sender.AddToPool(self.pgt_sender.GetMetricsStr('friends_online_stats', tags, str(user_online)))
                if int(state) == user_online:
                    continue

            if user_online == 0:
                db.InsertOffline(self.DB, user_id, timestamp, user_last_seen, False)
            elif user_online == 1:
                db.InsertOnline(self.DB, user_id, timestamp, False)

        self.DB.commit()
        if self.CONFIG.PROMETHEUS_SEND:
            self.pgt_sender.SendFromPool()

        if self.is_running:
            self.ceck_timer.start()

    def _updateDopUsers(self):
        if self.CONFIG.HAS_UPSER_FILE:
            fs_tools.GetIdList(self.CONFIG.USERS_FILE)

    def GetUnixTimestamp(self):
        return datetime.now().timestamp()

    def _handleExit(self, sig, frame):
        self.is_running = False
        print('Stopping')


if __name__ == '__main__':
    app = Main()
    app.Start()