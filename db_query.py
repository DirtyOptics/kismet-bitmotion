import sqlite3
import time
from tabulate import tabulate  # This is a library to make the output more readable; install with `pip install tabulate`

# Specify the path to your database
database_path = "/home/db/kismet-bitmotion/kismet_data.db"  # Replace with the absolute path

def fetch_latest_observations(limit=20):
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Query to fetch the last `limit` results, ordered by timestamp
    cursor.execute("""
        SELECT ssid, signal_dbm, gps_latitude, gps_longitude, timestamp 
        FROM ap_observations 
        ORDER BY id DESC 
        LIMIT ?
    """, (limit,))

    # Fetch the results
    results = cursor.fetchall()
    
    # Close the connection
    conn.close()

    return results

def monitor_database(interval=5, limit=20):
    try:
        while True:
            # Fetch the latest observations
            results = fetch_latest_observations(limit=limit)

            # Clear the terminal (optional, for better readability)
            print("\033c", end="")

            # Display the results using tabulate for a cleaner format
            headers = ["SSID", "Signal (dBm)", "Latitude", "Longitude", "Timestamp"]
            print(tabulate(results, headers=headers, tablefmt="pretty"))

            # Wait for the specified interval before querying again
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")

if __name__ == "__main__":
    monitor_database(interval=5, limit=20)
