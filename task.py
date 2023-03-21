import psycopg2
import io
import csv
import requests
from psycopg2 import sql

host = 'ethreum-rds.cluster-crwz9eu9x7fl.ap-south-1.rds.amazonaws.com'
database = 'dev'
username = 'price_data_read_user'
password = 'B9c1UNF62jjZ'

conn = psycopg2.connect(
    host=host,
    database=database,
    user=username,
    password=password
)

# total rows = 65252874
query = "SELECT * FROM {table} LIMIT 7000 OFFSET 0;"

cursor=conn.cursor()
cursor.execute(
    sql.SQL(query)
    .format(table=sql.Identifier('btcusdt-ochlv')))
col_names =[desc[0] for desc in cursor.description]

with open('dataminute.csv',mode='w',newline='') as file:
    writer = csv.writer(file)
    writer.writerow(col_names)

with open('dataminute.csv',mode='a',newline='') as file:
    writer = csv.writer(file)
    for row in cursor.fetchall():
        writer.writerow(row)
cursor.close()
conn.close()