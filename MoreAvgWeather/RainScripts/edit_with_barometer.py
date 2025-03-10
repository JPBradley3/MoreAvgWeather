import sqlite3
import math
import logging
import sys

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to calculate barometric pressure
def calculate_barometric_pressure(temperature, humidity, altitude):
    # Convert temperature to Kelvin
    temp_kelvin = float(temperature) + 273.15
    # Constants
    p0 = 1013.25  # Sea level standard atmospheric pressure (hPa)
    g = 9.80665  # Gravitational acceleration (m/s^2)
    L = 0.0065  # Temperature lapse rate (K/m)
    R = 8.31447  # Universal gas constant (J/(mol*K))
    M = 0.0289644  # Molar mass of dry air (kg/mol)
    # Calculate barometric pressure
    pressure = p0 * math.exp((-g * M * altitude) / (R * temp_kelvin))
    return pressure

# Function to convert temperature string to float
def convert_temperature(temp_str):
    if temp_str is None or temp_str == "N/A":
        return None  # Return None for invalid temperature entries
    try:
        # Attempt to convert directly to float
        return float(temp_str)
    except ValueError:
        if '°F' in temp_str:
            # Remove '°F' and convert to Celsius
            temp_fahrenheit = float(temp_str.replace('°F', ''))
            temp_celsius = (temp_fahrenheit - 32) * 5.0/9.0
            return temp_celsius
        elif '°C' in temp_str:
            # Remove '°C' and convert to float
            return float(temp_str.replace('°C', ''))
        else:
            raise ValueError(f"Unknown temperature format: {temp_str}")

# Function to convert humidity string to float
def convert_humidity(humidity_str):
    if isinstance(humidity_str, float):
        return humidity_str  # Return the value if it's already a float
    try:
        # Remove '%' and convert to float
        return float(humidity_str.replace('%', ''))
    except ValueError:
        raise ValueError(f"Unknown humidity format: {humidity_str}")

# Connect to the SQLite database
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()

# Check if the altitude column exists
cursor.execute("PRAGMA table_info(weather_data)")
columns = [column_info[1] for column_info in cursor.fetchall()]
if 'altitude' not in columns:
    logging.error('Altitude column does not exist in the weather_data table.')
    conn.close()
    sys.exit(1)

# Check if the barometric_pressure column already exists
if 'barometric_pressure' not in columns:
    cursor.execute("ALTER TABLE weather_data ADD COLUMN barometric_pressure REAL")
    conn.commit()

# Query the data from the database
try:
    cursor.execute("SELECT id, temperature, humidity, altitude FROM weather_data")
    data = cursor.fetchall()
except sqlite3.OperationalError as e:
    logging.error(f'SQL error: {e}')
    conn.close()
    sys.exit(1)

# Process the data
for row in data:
    entry_id = row[0]
    temperature = convert_temperature(row[1])
    if temperature is None:
        logging.warning(f'Skipping entry ID {entry_id}: Invalid temperature')
        continue  # Skip entries with invalid temperature
    humidity = convert_humidity(row[2])
    if humidity is None:
        logging.warning(f'Skipping entry ID {entry_id}: Invalid humidity')
        continue  # Skip entries with invalid humidity
    altitude = row[3]
    if altitude is None:
        logging.warning(f'Skipping entry ID {entry_id}: Invalid altitude')
        continue  # Skip entries with invalid altitude
    altitude = float(altitude)
    
    try:
        barometric_pressure = calculate_barometric_pressure(temperature, humidity, altitude)
        cursor.execute("UPDATE weather_data SET barometric_pressure = ? WHERE id = ?", (barometric_pressure, entry_id))
        logging.info(f'Updated entry ID {entry_id} with barometric pressure {barometric_pressure}')
    except Exception as e:
        logging.error(f'Failed to update entry ID {entry_id}: {e}')

# Commit the changes and close the connection
conn.commit()
conn.close()

logging.info('Barometric pressure added for each entry.')
