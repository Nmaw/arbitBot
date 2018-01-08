#TODO Create db sqlite or mongo
#TODO Write new informations about pairs and price
#TODO Read informations for analytics price


import sqlite3

import sys


class SQLite:

    def __init__(self):
        pass

    def __del__(self):
        pass

    @staticmethod
    def create_db(exchange, logger):
        dbfile = 'data/'.__add__(exchange.__add__('.sqlite'))
        conn = sqlite3.connect(dbfile)
        logger.info('Database {} was created with connect {}'.format(dbfile, conn))
        conn.close()

    def create_table(self, conn, cursor, name, logger):
        """
        :param conn: Connection to database
        :param logger: Logging for debug
        :param cursor: Cursor to database
        :param name: Name of table
        """
        print(conn, cursor, [(name,),])
        try:
            cursor.execute('CREATE TABLE IF NOT EXISTS symbols (x INTEGER, y, z, PRIMARY KEY(x ASC));')
            #cursor.execute('CREATE TABLE IF NOT EXISTS btcusd (x INTEGER, y, z, PRIMARY KEY(x ASC));')
        except sqlite3.DatabaseError as err:
            logger.error('Error create table: {}'.format(err))
            sys.exit()
        else:
            conn.commit()
        logger.info('Create table {} for connection {}'.format(name, conn))

    @staticmethod
    def connect(exchange, logger):
        dbfile = 'data/'.__add__(exchange.__add__('.sqlite'))
        conn = sqlite3.connect(dbfile)
        cursor = conn.cursor()
        logger.info('Connected {} to database {} with cursor {}'.format(conn, dbfile, cursor))
        return conn, cursor

    @staticmethod
    def close(conn):
        conn.close()

    @staticmethod
    def read(cursor, pair, data):
        print('Read data from DB:', cursor, pair, data)
        cursor.execute("SELECT Name FROM Artist ORDER BY Name LIMIT 3")
        result = cursor.fetchall()
        return result

    @staticmethod
    def write(conn, cursor, pair, data):
        print('Write date to DB:', cursor, pair, data)

    # Обратите внимание, даже передавая одно значение - его нужно передавать кортежем!
    # Именно по этому тут используется запятая в скобках!
        new_artists = [
            ('A Aagrh!',),
            ('A Aagrh!-2',),
            ('A Aagrh!-3',),
        ]

        try:
            cursor.executemany("insert into Artist values (Null, ?);", new_artists)
        except sqlite3.DatabaseError as err:
            print("Error: ", err)
        else:
            conn.commit()
