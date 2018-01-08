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
        cursor = conn.cursor()
        logger.info('Database {} was created with connect {} and cursor {}'.format(dbfile, conn, cursor))

        try:
            cursor.execute('CREATE TABLE IF NOT EXISTS symbols_details (pair text, price_precision real, initial_margin real, minimum_margin real, maximum_order_size real, minimum_order_size real, expiration text, PRIMARY KEY(pair ASC));')

        except sqlite3.DatabaseError as err:
            logger.error('Error: {} create tables in database: {} '.format(err, dbfile))
            sys.exit()
        else:
            conn.commit()
        logger.info('Create all tables for database {}'.format(exchange))
        conn.close()

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
    def insert(conn, cursor, table, data, logger):
        """
        :param table: where write
        :param conn: Connection
        :param cursor: Cursor
        :param data: Structure with data from exchange
        :return:
        """
        # print(data)
        if table == 'symbols_details':
            try:
                cursor.executemany('insert into symbols_details values ('
                                   ':pair, '
                                   ':price_precision, '
                                   ':initial_margin, '
                                   ':minimum_margin, '
                                   ':maximum_order_size, '
                                   ':minimum_order_size, '
                                   ':expiration);', data)
            except sqlite3.DatabaseError as err:
                logger.error('Error: {} insert table to {}'.format(err, table))
                # sys.exit()
            else:
                conn.commit()
            logger.info('Insert table {} for connection {}'.format(table, conn))
        else:
            logger.info('We have not information for table: {} and no write data.', table)
