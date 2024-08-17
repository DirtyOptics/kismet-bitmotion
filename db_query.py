import sqlite3

# Connect to the database
conn = sqlite3.connect('kismet-bitmotion/kismet_data.db')
cursor = conn.cursor()

# Query to fetch the table schema
cursor.execute("PRAGMA table_info(ap_observations)")

# Fetch and print the results
columns = cursor.fetchall()

for column in columns:
    print(column)

conn.close()
