import psycopg2
from psycopg2 import Error
import datetime
from read_and_transform import *

## setting up the connection with the postgres database
connection = psycopg2.connect(user="postgres",
                                    password="postgres",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="postgres")

cursor = connection.cursor()

# starting the main process of continually going through the queue, deleteing the message just read and 
# adding to the database. 

while True:
    new_message = read_and_transform()
    if new_message:
        postgres_insert_query = """ INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) VALUES (%s,%s,%s,%s,%s,%s,%s)"""
        record_to_insert = (new_message['user_id'], 
                            new_message['device_type'], 
                            new_message['ip'], 
                            new_message['device_id'], 
                            new_message['locale'],
                            int(new_message['app_version'].replace(".", "")), 
                            datetime.date.today())

        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()

        delete_from_top(new_message['receipt_handle'])
    else:
        break


# sanity check- checking the table to make sure the data was put into the queue

postgreSQL_select_Query = "select * from user_logins"

cursor.execute(postgreSQL_select_Query)
mobile_records = cursor.fetchall()

print("Print each row and it's columns values")
for row in mobile_records:
    print(row)
