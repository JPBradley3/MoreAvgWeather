import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('rain_data.db')
cursor = conn.cursor()

# Query to select all data from the RainData table
query = 'SELECT * FROM RainData'

# Execute the query and fetch all results
cursor.execute(query)
results = cursor.fetchall()

# Close the database connection
conn.close()

# Print the results in a readable format
print(f"{'ID':<5} {'Neighborhood':<20} {'Street':<35} {'Avg Density':<15} {'Rain Detected':<15} {'Timestamp'}")
print("=" * 105)

for row in results:
    id, neighborhood, street, average_density, rain_detected, timestamp = row
    rain_detected = 'True' if rain_detected else 'False'
    print(f"{id:<5} {neighborhood:<20} {street:<35} {average_density:<15.2f} {rain_detected:<15} {timestamp}")

