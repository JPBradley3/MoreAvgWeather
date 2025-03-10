import requests
from bs4 import BeautifulSoup
import sqlite3
import re
import logging

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

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

def clean_data(value):
    if isinstance(value, str):
        # Remove all non-numeric characters
        cleaned_value = re.sub(r'[^0-9.]', '', value)
        try:
            return float(cleaned_value)
        except ValueError:
            return None
    return value

def scrape_weather_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract temperature
        temperature_tag = soup.find('p', class_='myforecast-current-lrg')
        temperature_f = temperature_tag.text if temperature_tag else 'N/A'
        
        # Convert temperature to Celsius and extract numerical value
        if temperature_f != 'N/A':
            temperature_f = float(re.findall(r'\d+', temperature_f)[0])
            temperature_c = (temperature_f - 32) * 5.0/9.0
        else:
            temperature_c = 'N/A'

        # Extract wind speed numerical value
        wind_speed_tag = soup.find('td', class_='text-right', string='Wind Speed')
        wind_speed = re.findall(r'\d+', wind_speed_tag.find_next('td').text)[0] if wind_speed_tag else 'N/A'

        # Extract humidity numerical value
        humidity_tag = soup.find('td', class_='text-right', string='Humidity')
        humidity = re.findall(r'\d+', humidity_tag.find_next('td').text)[0] if humidity_tag else 'N/A'

        # Clean the data
        temperature_c = clean_data(temperature_c)
        wind_speed = clean_data(wind_speed)
        humidity = clean_data(humidity)

        return temperature_c, wind_speed, humidity
    except requests.RequestException as e:
        logging.error(f"Error fetching data from {url}: {e}")
        return None, None, None

def store_weather_data(db_name, location, temperature, wind_speed, humidity):
    logging.info(f"Storing data for {location} - Temperature: {temperature}, Wind Speed: {wind_speed}, Humidity: {humidity}")
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''CREATE TABLE IF NOT EXISTS weather_data (
                            id INTEGER PRIMARY KEY,
                            location TEXT,
                            temperature REAL,
                            wind_speed REAL,
                            humidity REAL,
                            barometric_pressure REAL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                          )''')

        # Insert weather data
        cursor.execute('''INSERT INTO weather_data (location, temperature, wind_speed, humidity)
                          VALUES (?, ?, ?, ?)''', (location, temperature, wind_speed, humidity))
        logging.info(f"Data for {location} inserted successfully.")

for location, coords in neighborhoods_coordinates.items():
    latitude = coords['latitude']
    longitude = coords['longitude']
    url = f'https://forecast.weather.gov/MapClick.php?lat={latitude}&lon={longitude}'

    temperature, wind_speed, humidity = scrape_weather_data(url)
    logging.info(f'{location} - Temperature: {temperature} °C, Wind Speed: {wind_speed} MPH, Humidity: {humidity} %')

    store_weather_data('weather_data.db', location, temperature, wind_speed, humidity)

logging.info('Weather data stored in weather_data.db')
