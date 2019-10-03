import configparser
import requests
import os

config = configparser.ConfigParser()
config.read("./config/config.conf")

SERVER_ADDRES = config['Prometheus']['host']

headers={'Content-type': 'text/plain; charset=utf-8'}

def SendMetrics(content: str):
    requests.post(SERVER_ADDRES, data=content.encode('utf-8'), headers=headers)
