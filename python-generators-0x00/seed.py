#!/usr/bin/python3

import mysql.connector
from mysql.connector import Error
import pandas as pd
import uuid

def connect_db():
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'bini'
        )

        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to the MySQL: {e}")
        return None

def create_database(connection):
    try:
        #Creating cursor to execute mysql commands
        cursor = connection.cursor()

        #SQL command to create new database
        cursor.execute('CREATE DATABASE IF NOT EXISTS ALX_prodev')
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = 'bini',
            database = 'ALX_prodev'
        )

        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error while connecting to 'ALX_prodev' Database: {e}")
        return None

def create_table(connection):
    try:
        cursor = connection.cursor()
        #SQL command to use the database already created
        cursor.execute('USE ALX_prodev')

        #SQL command to create new table
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) NOT NULL,
                age DECIMAL(5, 2) NOT NULL,
                INDEX(user_id)
            )
        """
        cursor.execute(create_table_sql)
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error while creating table: {e}")
def insert_data(connection, data):
    try:
        #SQL command to insert data to a table
        cursor = connection.cursor()
        for index, row in pd.read_csv(data).iterrows():
            user_id = str(uuid.uuid4())
            insert_query = """
                INSERT INTO user_data(user_id, name, email, age)
                VALUES(%s, %s, %s, %s)
            """
            values = (user_id, row['name'], row['email'], float(row['age']))
            cursor.execute(insert_query, values)
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error while inserting data: {e}")

if __name__ == "__main__":
    try:
        conn = connect_db()
        if conn:
            create_database(conn)
            conn.close()

        conn_prodev = connect_to_prodev()
        if connect_to_prodev:
            create_table(conn_prodev)
            insert_data(conn_prodev, 'user_data.csv')
            conn_prodev.close()
    except Error as e:
        print(f"Unexpected error {e}")