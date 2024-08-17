import sqlite3
from tabulate import tabulate

# Specify the path to your database
database_path = "/home/db/kismet-bitmotion/kismet_data.db"  # Replace with the absolute path

# Connect to the SQLite database
conn = sqlite3.connect(database_path)
cursor = conn.cursor()

# Query to fetch observations for a specific BSSID over time
cursor.execute("""
    SELECT ssid, bssid, signal_dbm, gps_latitude, gps_longitude, timestamp 
    FROM ap_observations 
    WHERE bssid = ? 
    ORDER BY timestamp DESC 
    LIMIT 20
""", ('74:83:C2:B2:D2:5D',))  # Replace with the BSSID you're interested in

# Fetch the results
results = cursor.fetchall()

# Display the results using tabulate for a cleaner format
headers = ["SSID", "BSSID", "Signal (dBm)", "Latitude", "Longitude", "Timestamp"]
print(tabulate(results, headers=headers, tablefmt="pretty"))

# Close the connection
conn.close()
