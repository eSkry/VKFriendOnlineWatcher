import requests
import os

SERVER_ADDRES = 'http://85.10.234.188:9091/metrics/job/VKFriendOnlineWatcher'


headers={'Content-type': 'text/plain; charset=utf-8'}

def SendMetrics(content: str):
    requests.post(SERVER_ADDRES, data=content.encode('utf-8'), headers=headers)
