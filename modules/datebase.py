#TODO Create db sqlite or mongo
#TODO Write new informations about pairs and price
#TODO Read informations for analytics price


import sqlite3


class SQLite:

    def __init__(self):
        pass

    def __del__(self):
        pass

    @staticmethod
    def create_db(exchange, logger):
        dbfile = 'data//'.__add__(exchange.__add__('.sqlite'))
        conn = sqlite3.connect(dbfile)
        logger.info('Database data/{}.sqlite was created with connect {}'.format(dbfile, conn))
        conn.close()

    def create_table(self, conn, cursor, pair):
        """
        :param conn: Connections to database
        :param cursor: Cursor for database
        :param pair: Pair crypto values
        """
        pass

    @staticmethod
    def connect(db):
        conn = sqlite3.connect(db.__add__('.sqlite'))
        cursor = conn.cursor()
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
