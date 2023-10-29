import sqlite3


def read_cnx(file):
    return sqlite3.connect(file)
