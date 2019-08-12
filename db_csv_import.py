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
        f.write('id,online,timestamp\n')
        table = db.getAllData(conn).fetchall()
        for row in table:
            f.write('{};{};{}\n'.format( row[1], row[2], row[3] ))


if __name__ == '__main__':
    importToCSV()