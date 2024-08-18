import psycopg2
import yaml
import time
from tabulate import tabulate

# Load configuration from YAML file
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

# Get the database URL from the config file
database_url = config.get("database_url")

def fetch_latest_observations(limit=50, retry_attempts=5, retry_delay=1):
    attempt = 0
    while attempt < retry_attempts:
        try:
            # Connect to the PostgreSQL database
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()

            # Query to fetch the last `limit` results, ordered by timestamp
            cursor.execute("""
                SELECT ssid, signal_dbm, gps_latitude, gps_longitude, timestamp 
                FROM ap_observations 
                ORDER BY id DESC 
                LIMIT %s
            """, (limit,))

            # Fetch the results
            results = cursor.fetchall()

            # Close the connection
            conn.close()

            return results

        except psycopg2.OperationalError as e:
            if "could not connect to server" in str(e):
                print(f"Database connection failed, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{retry_attempts})")
                time.sleep(retry_delay)
                attempt += 1
            else:
                raise
    print("Failed to fetch data after multiple attempts.")
    return []

def monitor_database(interval=5, limit=50):
    try:
        while True:
            # Fetch the latest observations
            results = fetch_latest_observations(limit=limit)

            # Clear the terminal (optional, for better readability)
            print("\033c", end="")

            if results:
                # Display the results using tabulate for a cleaner format
                headers = ["SSID", "Signal (dBm)", "Latitude", "Longitude", "Timestamp"]
                print(tabulate(results, headers=headers, tablefmt="pretty"))
            else:
                print("No data to display or database was locked.")

            # Wait for the specified interval before querying again
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")

if __name__ == "__main__":
    monitor_database(interval=5, limit=50)
