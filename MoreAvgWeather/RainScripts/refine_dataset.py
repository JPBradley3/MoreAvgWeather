import sqlite3
import requests
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Tomorrow.io API key
API_KEY = 'Enter Yours Here'  # Replace with your actual API key

# Coordinates for neighborhoods
neighborhoods_coordinates = {
    "Capitol Hill": {"latitude": 47.6062, "longitude": -122.3321},
    "Ballard": {"latitude": 47.6685, "longitude": -122.3815},
    "Fremont": {"latitude": 47.6536, "longitude": -122.3509},
    "University District": {"latitude": 47.6588, "longitude": -122.3127},
    "Queen Anne": {"latitude": 47.6290, "longitude": -122.3570},
    "Wallingford": {"latitude": 47.6556, "longitude": -122.3370},
    "Woodland Park Zoo": {"latitude": 47.6694, "longitude": -122.3515},
    "KOMO News": {"latitude": 47.6187, "longitude": -122.3588},
    "KIRO News": {"latitude": 47.6251, "longitude": -122.3341},
    "KEXP": {"latitude": 47.6317, "longitude": -122.3576},
    "Alki Beach": {"latitude": 47.5785, "longitude": -122.4156},
    "Central District": {"latitude": 47.5985, "longitude": -122.3001},
    "Madrona": {"latitude": 47.6074, "longitude": -122.2892},
    "Magnolia": {"latitude": 47.6447, "longitude": -122.4004},
    "Interbay": {"latitude": 47.6545, "longitude": -122.3705}
}

# Function to fetch weather data from Tomorrow.io
def fetch_tomorrowio_data(latitude, longitude, retries=3, backoff_factor=1):
    url = f"https://api.tomorrow.io/v4/timelines"
    querystring = {
        "location": f"{latitude},{longitude}",
        "fields": ["precipitationProbability"],
        "timesteps": "1m",
        "units": "metric",
        "apikey": API_KEY
    }
    for attempt in range(retries):
        response = requests.get(url, params=querystring)
        if response.status_code == 429:  # Too Many Requests
            sleep_time = backoff_factor * (2 ** attempt)
            logging.warning(f"Rate limit exceeded. Retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
        else:
            break
    data = response.json()
    return data

# Connect to your SQLite database
db_path = r"C:\Users\Parker\Documents\project\weather_data.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add a column for Tomorrow.io precipitation probability if it doesn't exist
cursor.execute("PRAGMA table_info(weather)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if 'tomorrowio_precipitation_probability' not in column_names:
    cursor.execute("ALTER TABLE weather ADD COLUMN tomorrowio_precipitation_probability REAL")

# Update database with Tomorrow.io data for each neighborhood
for neighborhood, coords in neighborhoods_coordinates.items():
    latitude = coords["latitude"]
    longitude = coords["longitude"]
    tomorrowio_data = fetch_tomorrowio_data(latitude, longitude)

    # Extract precipitation probability with error handling
    try:
        precipitation_probability = tomorrowio_data['data']['timelines'][0]['intervals'][0]['values']['precipitationProbability']
        cursor.execute("UPDATE weather SET tomorrowio_precipitation_probability = ? WHERE neighborhood = ?", (precipitation_probability, neighborhood))
    except KeyError as e:
        logging.error(f"KeyError: {e} for neighborhood: {neighborhood} with data: {tomorrowio_data}")

# Commit the changes and close the connection
conn.commit()
conn.close()

logging.info("Tomorrow.io precipitation probability fetched and updated for each neighborhood.")
