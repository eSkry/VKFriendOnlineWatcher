import psycopg2
import os

# Return true if file exists
def IsFileExists(file):
    return os.path.exists(file) and os.path.isfile(file)

# Reading file to string and return his
def ReadAllFile(file: str):
    if IsFileExists(file):
        f = open(file, 'r')
        data = f.read()
        f.close()
        return data
    else:
        return None

def CreateDb(dbName, host, user, password, initsqlfile):
    conn = psycopg2.connect(dbname=dbName, host=host, user=user, password=password)
    cur = conn.cursor()
    conn.autocommit = True
    sqliscript = ReadAllFile(initsqlfile)
    if sqliscript:
        cur.execute(sqliscript)
    cur.close()



