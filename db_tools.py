import sqlite3
import os


DB_NAME = 'db.db'

# Reading file to string and return his
def ReadAllFile(file: str):
    if IsFileExists(file):
        f = open(file, 'r')
        data = f.read()
        f.close()
        return data
    else:
        return ''

# Return true if file exists
def IsFileExists(file):
    return os.path.exists(file) and os.path.isfile(file)


def CreateDB(sql_file: str, db_name = DB_NAME):
    if (IsFileExists(db_name)):
        return sqlite3.connect(db_name, isolation_level=None)

    try:
        conn = sqlite3.connect(db_name)
    except:
        print('Db create error')

    if IsFileExists(sql_file):
        sql = ReadAllFile(sql_file)
        conn.executescript(sql)

    return conn


def GetLastState(conn: sqlite3.Connection, user_id):
    return conn.execute('SELECT *, max(timestamp) FROM statistics WHERE user_id = {}'.format(user_id))


def InsertMetrics(conn: sqlite3.Connection, metrics):
    for key in metrics.keys():
        conn.execute('INSERT INTO statistics (user_id, online, timestamp) VALUES ({}, {}, {});'
                    .format( metrics[key]['id'], metrics[key]['online'], metrics[key]['timestamp'] ))
        
    conn.commit()

def InsertOnline2(conn: sqlite3.Connection, user_id, timestamp): # Создает новую запись
    conn.execute('INSERT INTO statistics (user_id, begin_online) VALUES ({}, {})'.format(user_id, timestamp))
    conn.commit()

def InsertOffline2(conn: sqlite3.Connection, user_id, timestamp): # обновляет запись добавляя в нее дату завершения сессии
    conn.execute('UPDATE statistics SET end_online = {} WHERE user_id = {} AND id = (SELECT max(id) FROM statistics)'.format(timestamp, user_id))
    conn.commit()

def GetLastState2(conn: sqlite3.Connection, user_id):
    cur = conn.execute('SELECT max(id) as id, begin_online, end_online FROM statistics WHERE user_id = {}'.format(user_id))
    data = cur.fetchone()

    if data == None:
        return None

    if data[1] != None and data[2] != None:
        return 0
    elif data[1] != None:
        return 1


def getAllData(conn: sqlite3.Connection):
    return conn.execute('SELECT * FROM statistics;')