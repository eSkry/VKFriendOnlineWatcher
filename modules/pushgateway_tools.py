import requests
import os

class PushgatewaySender(object):
    def __init__(self, server_addres):
        self.SERVER_ADDRES = server_addres
        self.HEADERS = {'Content-type': 'text/plain; charset=utf-8'}
        self.METRICKS_POOL = []

    def AddToPool(self, metricks_string: str):
        self.METRICKS_POOL.append(str)

    def SendFromPool(self):
        self._sendData(''.join(self.METRICKS_POOL))
        self.METRICKS_POOL.clear()

    def GetMetricsStr(self, name, tags: dict, value, timestamp = ''):
        data_line = "{} {{".format(name)

        kv = []
        for key, value in tags.items():
            kv.append('{}="{}"'.format(key, value))

        data_line += ', '.join(kv)
        data_line += "}} {} {}\n".format(value, timestamp)
        return data_line

    def SendMetrick(self, metrick: str):
        self._sendData(metrick)

    def _sendData(self, content: str):
        requests.post(self.SERVER_ADDRES, data=content.encode('utf-8'), headers=self.HEADERS)
