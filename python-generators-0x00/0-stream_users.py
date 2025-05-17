#!/usr/bin/python3

import json

seed = __import__('seed')

def stream_users():
    connect = seed.connect_to_prodev()
    if connect:
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM user_data")
        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield "{'user_id'" + ": " + row[0] + ", 'name'" + ": " + row[1] + ", 'email'" + ": " + row[2] + ", 'age'" + ":" + str(float(row[3])) + "}"
        cursor.close()

if __name__ == "__main__":
    connection = seed.connect_to_prodev()
    if connection:
        for user in stream_users():
            json_user = json.dumps(user, default=str, indent=4)
            print(json_user)
            
        connection.close()