import sqlite3
import os

import db_tools


def migration1():
    print('Предпологается что в файле init.sql лежит информаци о версии БД на которую происходит миграция')
    print('Start magration from (id, user_id, online, timestamp) to (id, user_id, begin_online, end_online)')
    
    old = sqlite3.connect(db_tools.DB_NAME, isolation_level=None)
    new = db_tools.CreateDB('init.sql', 'new_db.db')
    
    allOldData = db_tools.getAllData(old) # OLD DATA


if __name__ == "__main__":
    migration1()

