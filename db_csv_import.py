from datetime import datetime
import sqlite3
import os

import db_tools as db


def importToCSV(conn: sqlite3.Connection, data):
    with open('resultcsv.csv', 'w') as f:
        f.write('id,online,timestamp')
        for id in data.keys():
            f.write( '{};{};{}'.format( id, data[id]['online'], data[id]['timestamp'] ) )


def importToCSV():
    conn = db.CreateDB('init.sql')

    with open('resultcsv.csv', 'w') as f:
        f.write('id;online;date;time\n')
        table = db.getAllData(conn).fetchall()
        for row in table:
            date = datetime.fromtimestamp(row[3])
            f.write('{};{};{};{}\n'.format( row[1], row[2], date.strftime('%d.%m.%Y'), date.strftime('%H:%M:%S') ))


if __name__ == '__main__':
    importToCSV()