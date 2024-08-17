import sqlite3
from tabulate import tabulate  # This is a library to make the output more readable; install with `pip install tabulate`

# Specify the path to your database
database_path = "/home/db/kismet-bitmotion/kismet_data.db"  # Replace with the absolute path

# Connect to the SQLite database
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Query to fetch the last 20 results, ordered by timestamp
cursor.execute("""
    SELECT ssid, signal_dbm, gps_latitude, gps_longitude, timestamp 
    FROM ap_observations 
    ORDER BY id DESC 
    LIMIT 20
""")

# Fetch the results
results = cursor.fetchall()

# Display the results using tabulate for a cleaner format
headers = ["SSID", "Signal (dBm)", "Latitude", "Longitude", "Timestamp"]
print(tabulate(results, headers=headers, tablefmt="pretty"))

# Close the connection
conn.close()
