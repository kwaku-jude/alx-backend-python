#!/usr/bin/python3

import json
import decimal

seed = __import__('seed')

def stream_users_in_batches(batch_size):
    connection = seed.connect_to_prodev()
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM user_data')
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                return
            yield batch
        cursor.close()

def batch_processing(batch_size):
    for batch in stream_users_in_batches(batch_size):
        filtered_user = [
            {**row, 'age': float(row['age'])}
            for row in batch
            if isinstance(row['age'], (int, float, decimal.Decimal)) and float(row['age']) > 25
        ]
        for user in filtered_user:
            print(json.dumps(user, indent=2))