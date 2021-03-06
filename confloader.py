import configparser
import os


class VKFOConfig(object):
    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read('./config/config.conf')

        self.VK_LOGIN = conf['Auth']['vk_login']
        self.VK_PASSWORD = conf['Auth']['vk_password']
        self.VK_TOKEN = None
        self.VK_APP_ID = None

        if conf.has_section('Prometheus'):
            self.PROMETHEUS_SEND = conf['Prometheus']['active'].lower() == "true"
            self.PROMETHEUS_HOST = conf['Prometheus']['host']
        else:
            self.PROMETHEUS_SEND = False

        if conf.has_option('Users', 'file'):
            self.HAS_UPSER_FILE = True
            self.USERS_FILE = conf['Users']['file']
        else:
            self.HAS_UPSER_FILE = False

        if conf.has_option('Auth', 'vk_app_id'):
            self.VK_APP_ID = None if conf['Auth']['vk_app_id'] == "None" else conf['Auth']['vk_app_id']

        if conf.has_option('Auth', 'vk_token'):
            self.VK_TOKEN =  None if conf['Auth']['vk_token'] == "None" else conf['Auth']['vk_token']
            