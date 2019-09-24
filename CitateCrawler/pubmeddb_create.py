from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode

import mysql.connector

DB_NAME = 'pubmeddb'
# DB_NAME = 'scopusdb'
cnx = mysql.connector.MySQLConnection(user='root', password='tmppwd',
                              host='127.0.0.1', database=DB_NAME)

TABLES = {}
TABLES['articles'] = (
    "CREATE TABLE IF NOT EXISTS `articles` ("
    "  `pmid` varchar(20),"
    "  `authors` text,"
    "  `title` text,"
    "  `abstract` text,"
    "  `publication_date` text,"
    "  `publication_type` text,"
    "  `publication_title` text,"
    "  `publication_issue` text,"
    "  `doi` text,"
    "  PRIMARY KEY (`pmid`)"
    ")")

cursor = cnx.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)
        exit(1)


for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cursor.close()
cnx.close()
