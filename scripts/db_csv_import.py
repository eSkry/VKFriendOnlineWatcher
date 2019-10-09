from datetime import datetime
import sqlite3
import os

from modules import db_sqlite as db

# def importToCSV(conn: sqlite3.Connection, data):
#     with open('resultcsv.csv', 'w') as f:
#         f.write('id,begin_online,end_online')
#         for id in data.keys():
#             f.write( '{};{};{}'.format( id, data[id]['online'], data[id]['timestamp'] ) )


def importToCSV():
    conn = db.CreateDB('init.sql')

    with open('resultcsv.csv', 'w') as f:
        f.write('id;begin_online;end_online\n')
        table = db.getAllData(conn).fetchall()
        for row in table:
            begin_session = datetime.fromtimestamp(row[2]).strftime('%d.%m.%Y %H:%M')
            end_session = ""

            if row[3] != None:
                end_session = datetime.fromtimestamp(row[3]).strftime('%d.%m.%Y %H:%M')
            else:
                end_session = None

            f.write('{};{};{}\n'.format( row[1], begin_session, end_session ))


if __name__ == '__main__':
    importToCSV()