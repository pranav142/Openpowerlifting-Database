import pandas as pd
import mysql.connector
from mysql.connector import Error


csv_file = "C:/Users/pknad/OneDrive/Documents/Machine_Learning/PowerLifting/data/processed/processed_lifting_data.csv"
df = pd.read_csv(csv_file)


import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="*",
        database="openpowerlifting",
    )

    if conn.is_connected():
        print("Connected to MySQL database")
except Error as e:
    print(f"Error connecting to MySQL database: {e}")
