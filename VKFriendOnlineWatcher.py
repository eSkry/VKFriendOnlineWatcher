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
        self.vk_session = vk_api.VkApi(login=self.CONFIG.VK_LOGIN, password=self.CONFIG.VK_PASSWORD)
        self.vk_session.auth(token_only=True)
        self.vkapi = self.vk_session.get_api()
        self.VK_USER_IDS = []
        self.DOP_USER_IDS = []
        self.dop_thread = threading.Thread(target=self.UpdateDopUsers)
        self.loop_thread = threading.Thread(target=self._loop)
        self.USE_LONGPOLL = False
        self.is_running = False

        if self.CONFIG.PROMETHEUS_SEND:
            self.pgt_sender = pgt.PushgatewaySender(self.CONFIG.PROMETHEUS_HOST)

        if self.CONFIG.HAS_UPSER_FILE:
            self.DOP_USER_IDS = fs_tools.GetIdList(self.CONFIG.USERS_FILE)

        signal.signal(signal.SIGINT, self._handleExit)
        signal.signal(signal.SIGTERM, self._handleExit)

    def Start(self):
        self.is_running = True
        self.dop_thread.start()
        if self.USE_LONGPOLL:
            self.longpoll = VkLongPoll(self.vk_session)
            self.loop_thread.start()

    def Stop(self):
        self.is_running = False

    def Wait(self):
        self.dop_thread.join()
        if self.USE_LONGPOLL:
            self.loop_thread.join()

    def _loop(self):
        conn = db.CreateDB('./sql/init.sql')
        for event in self.longpoll.listen():
            if not self.is_running:
                break

            tags = { 'user': event.user_id, 'full_name': event.full_name, 'platform': event.last_seen }
            if event.type == VkEventType.USER_ONLINE:
                db.InsertOnline(conn, event.user_id, event.timestamp)
                self.pgt_sender.AddToPool(self.pgt_sender.GetMetricsStr('friends_online_stats', tags, '1'))
            elif event.type == VkEventType.USER_OFFLINE:
                db.InsertOffline(conn, event.user_id, event.timestamp, event.last_seen)
                self.pgt_sender.AddToPool(self.pgt_sender.GetMetricsStr('friends_online_stats', tags, '0'))
            
            if event.user_id not in self.VK_USER_IDS:
                self.VK_USER_IDS.append(event.user_id)
                db.AddNewUser(conn, event.user_id, event.full_name)

    def UpdateDopUsers(self):
        conn = db.CreateDB('./sql/init.sql')
        while self.is_running:
            dop_users = self.vkapi.users.get(user_uds=self.DOP_USER_IDS, fields=['online', 'last_seen'])

            if not self.USE_LONGPOLL:
                friends = self.vkapi.friends.get(fields=['online', 'last_seen'])['items']
                dop_users = dop_users + friends

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
                    if not db.IsUserExists(conn, user_id):
                        db.AddNewUser(conn, user_id, full_name, False)

                state = db.GetLastState(conn, user_id)
                if state != None:
                    if self.CONFIG.PROMETHEUS_SEND:
                        tags = { 'user': user_id, 'full_name': full_name, 'platform': user_last_seen }
                        self.pgt_sender.AddToPool(self.pgt_sender.GetMetricsStr('friends_online_stats', tags, str(user_online)))
                    if int(state) == user_online:
                        continue

                if user_online == 0:
                    db.InsertOffline(conn, user_id, timestamp, user_last_seen, False)
                elif user_online == 1:
                    db.InsertOnline(conn, user_id, timestamp, False)

            conn.commit()
            if self.CONFIG.PROMETHEUS_SEND:
                self.pgt_sender.SendFromPool()
            
            self._waiter()

    def _waiter(self):
        UPD_SECONDS = 60
        i = 0
        while self.is_running and i < UPD_SECONDS:
            i = i + 1
            time.sleep(1)

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
    app.Wait()