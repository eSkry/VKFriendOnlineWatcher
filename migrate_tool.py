import sqlite3
import sys
import os

import db_tools


def migration1():
    print('Предпологается что в файле init.sql лежит информаци о версии БД на которую происходит миграция')
    print('Start magration from (id, user_id, online, timestamp) to (id, user_id, begin_online, end_online)')
    
    olddb = sqlite3.connect(db_tools.DB_NAME, isolation_level=None)
    newdb = db_tools.CreateDB('init.sql', 'new_db.db')
    
    user_ids_cur = olddb.execute('SELECT DISTINCT user_id FROM statistics')
    for usr in user_ids_cur:
        user_id = usr[0]
        user_metrics_cur = olddb.execute('SELECT * FROM statistics WHERE user_id = {} ORDER BY id'.format(user_id))

        print('user={}'.format(user_id))

        isFirst = True # Первая запись (для выравнивания)
        isBegin = True 
        i = 0
        for row in user_metrics_cur:
            i = i + 1
            sys.stdout.write('\r Step {}'.format(i))
            sys.stdout.flush()

            if isFirst and row[2] == 0:
                isFirst = False
                continue
            isFirst = False

            if isBegin:
                db_tools.InsertOnline2(newdb, user_id, row[3], False)
                isBegin = False
            else:
                db_tools.InsertOffline2(newdb, user_id, row[3], False)
                isBegin = True

        newdb.commit()
        print('\n')



if __name__ == "__main__":
    migration1()

