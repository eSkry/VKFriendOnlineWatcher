import requests
import os

SERVER_ADDRES = 'http://85.10.234.188:9091/metrics/job/VKFriendOnlineWatcher'


headers = {"Content-type": "application/x-www-form-urlencoded",
            "Accept": "text/plain"}


def SendMetrics(content: str):
    requests.post(SERVER_ADDRES, data=content)
