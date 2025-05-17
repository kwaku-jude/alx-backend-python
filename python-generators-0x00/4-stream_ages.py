#!/usr/bin/python3

import decimal

seed = __import__('seed')

def stream_user_ages():
    connection = seed.connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM user_data')

    while True:
        row = cursor.fetchone()
        if row is None:
            break
        age = row[3]
        if isinstance(age, decimal.Decimal):
            age = float(age)
        yield age
    cursor.close()

def calculate_average_age():
    total_age = 0.0
    count = 0

    for age in stream_user_ages():
        total_age += age
        count += 1

    if count > 0:
        average = total_age/count
        print(f"Average age of users: {average: .2f}")

if __name__ == "__main__":
    connection = seed.connect_to_prodev()
    if connection:
        calculate_average_age() 
        connection.close()