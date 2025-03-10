import sqlite3
import requests
import logging
import time

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Replace 'YOUR_API_KEY' with your actual Google Maps Elevation API key
API_KEY = 'AIzaSyAaRt4kmjgz8m4KaM9KQSA1mGZubviGy1E'
ELEVATION_API_URL = 'https://maps.googleapis.com/maps/api/elevation/json'

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

def get_altitude(lat, lng, api_key):
    """Get the altitude for given latitude and longitude using Google Maps Elevation API."""
    url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lng}&key={api_key}"
    logging.info(f"Requesting altitude for lat: {lat}, lng: {lng} with URL: {url}")
    
    response = requests.get(url)
    result = response.json()
    
    if result['status'] == 'OK':
        return result['results'][0]['elevation']
    else:
        logging.error(f"Error fetching altitude: {result['status']} - {result.get('error_message', 'No error message')}")
        return None

def update_database_with_altitude(db_path, api_key):
    """Update the SQLite database with altitude data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if necessary columns exist, and add them if not
    cursor.execute("PRAGMA table_info(weather_data)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'latitude' not in columns:
        cursor.execute("ALTER TABLE weather_data ADD COLUMN latitude REAL")
    if 'longitude' not in columns:
        cursor.execute("ALTER TABLE weather_data ADD COLUMN longitude REAL")
    if 'neighborhood' not in columns:
        cursor.execute("ALTER TABLE weather_data ADD COLUMN neighborhood TEXT")
    if 'altitude' not in columns:
        cursor.execute("ALTER TABLE weather_data ADD COLUMN altitude REAL")

    # Fetch and update altitude for each neighborhood
    for name, coords in neighborhoods_coordinates.items():
        lat, lng = coords['latitude'], coords['longitude']
        try:
            altitude = get_altitude(lat, lng, api_key)
            if altitude is not None:
                cursor.execute("""
                UPDATE weather_data
                SET latitude = ?, longitude = ?, altitude = ?, neighborhood = ?
                WHERE location = ?
                """, (lat, lng, altitude, name, name))
                conn.commit()
                logging.info(f"Updated {name} with altitude {altitude}")
            time.sleep(1)  # Add delay to avoid hitting rate limits
        except Exception as e:
            logging.error(f"Failed to update {name}: {e}")

    conn.close()

if __name__ == "__main__":
    db_path = 'weather_data.db'
    api_key = API_KEY
    update_database_with_altitude(db_path, api_key)
