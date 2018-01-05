#TODO Create db sqlite or mongo
#TODO Write new informations about pairs and price
#TODO Read informations for analytics price


import sqlite3


def create_db(exchange):
    dbfile = 'data//'.__add__(exchange.__add__('.sqlite'))
    conn = sqlite3.connect(dbfile)
    conn.close()


def create_table(conn, cursor, pair):
    pass


def connect(db):
    conn = sqlite3.connect(db.__add__('.sqlite'))
    cursor = conn.cursor()
    return conn, cursor


def close(conn):
    conn.close()


def read(cursor, pair, data):
    print('Read data from DB:', cursor, pair, data)
    cursor.execute("SELECT Name FROM Artist ORDER BY Name LIMIT 3")
    result = cursor.fetchall()
    return result


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
