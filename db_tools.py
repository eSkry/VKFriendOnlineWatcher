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


def CreateDB(sql_file: str):
    if (IsFileExists(DB_NAME)):
        return sqlite3.connect(DB_NAME, isolation_level=None)

    conn = sqlite3.connect(DB_NAME)

    if IsFileExists(sql_file):
        sql = ReadAllFile(sql_file)
        conn.executescript(sql)

    return conn



def insertMetrics(conn: sqlite3.Connection, metrics):
    for key in metrics.keys():
        conn.execute('INSERT INTO statistics (user_id, online, timestamp) VALUES ({}, {}, {});'
                    .format( metrics[key]['id'], metrics[key]['online'], metrics[key]['timestamp'] ))
        
    conn.commit()


def getAllData(conn: sqlite3.Connection):
    return conn.execute('SELECT * FROM statistics;')
    