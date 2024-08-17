import sqlite3
from prettytable import PrettyTable

# Connect to the database
conn = sqlite3.connect('kismet-bitmotion/kismet_data.db')
cursor = conn.cursor()

# Query for a specific BSSID
bssid_to_query = "74:83:C2:B2:D2:5D"  # Replace with the BSSID you want to check
cursor.execute("SELECT ssid, signal_dbm, first_seen FROM ap_observations WHERE bssid = ?", (bssid_to_query,))

# Fetch all results
results = cursor.fetchall()

# Print results in a table format
table = PrettyTable(["SSID", "Signal (dBm)", "First Seen"])
for row in results:
    table.add_row(row)

print(table)

conn.close()
