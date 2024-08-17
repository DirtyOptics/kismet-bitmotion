import sqlite3

# Connect to the database
conn = sqlite3.connect('kismet-bitmotion/kismet_data.db')
cursor = conn.cursor()

# Specify the BSSID you want to query
bssid_to_query = 'YOUR_BSSID_HERE'  # Replace with the BSSID you're interested in

# Execute the query to fetch the necessary fields
cursor.execute("""
    SELECT ssid, signal_dbm, gps_latitude, gps_longitude, timestamp 
    FROM ap_observations 
    WHERE bssid = ?
    ORDER BY timestamp ASC
""", (bssid_to_query,))

# Fetch and print the results
observations = cursor.fetchall()

for observation in observations:
    print(f"SSID: {observation[0]}, Signal: {observation[1]} dBm, Latitude: {observation[2]}, Longitude: {observation[3]}, Timestamp: {observation[4]}")

conn.close()
