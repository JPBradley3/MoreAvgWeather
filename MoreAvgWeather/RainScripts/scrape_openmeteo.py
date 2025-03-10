import requests
import sqlite3
import datetime

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

def scrape_weather_data(latitude, longitude):
    url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,wind_speed_10m,relative_humidity_2m'
    response = requests.get(url)

    # Print the raw response text for debugging
    print(f'Response for coordinates ({latitude}, {longitude}): {response.text}')

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        print(f'Error: Unable to decode JSON response for coordinates: {latitude}, {longitude}')
        return 'N/A', 'N/A', 'N/A'
    
    if 'hourly' in data and 'temperature_2m' in data['hourly'] and 'wind_speed_10m' in data['hourly'] and 'relative_humidity_2m' in data['hourly']:
        temperature = data['hourly']['temperature_2m'][0]
        wind_speed = data['hourly']['wind_speed_10m'][0]
        humidity = data['hourly']['relative_humidity_2m'][0]
    else:
        temperature = wind_speed = humidity = 'N/A'
        print(f'Error: Invalid data for coordinates: {latitude}, {longitude} - Response: {data}')
        
    return temperature, wind_speed, humidity

def store_weather_data(db_name, location, temperature, wind_speed, humidity):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                        id INTEGER PRIMARY KEY,
                        location TEXT,
                        temperature TEXT,
                        wind_speed TEXT,
                        humidity TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                      )''')

    # Insert weather data
    cursor.execute('''INSERT INTO weather_data (location, temperature, wind_speed, humidity)
                      VALUES (?, ?, ?, ?)''', (location, temperature, wind_speed, humidity))

    # Commit and close the connection
    conn.commit()
    conn.close()

db_name = 'weather_data.db'

for location, coords in neighborhoods_coordinates.items():
    latitude = coords['latitude']
    longitude = coords['longitude']
    
    temperature, wind_speed, humidity = scrape_weather_data(latitude, longitude)
    print(f'{location} - Temperature: {temperature}, Wind Speed: {wind_speed}, Humidity: {humidity}')

    store_weather_data(db_name, location, temperature, wind_speed, humidity)

print(f'Weather data stored in {db_name}')
