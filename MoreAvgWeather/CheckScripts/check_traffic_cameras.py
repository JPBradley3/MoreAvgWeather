import requests
import cv2
import numpy as np
import sqlite3
import re
from datetime import datetime
import pyproj

# Create or connect to SQLite database
conn = sqlite3.connect('rain_data.db')
cursor = conn.cursor()

# Drop the existing RainData table if it exists (for testing purposes)
cursor.execute('DROP TABLE IF EXISTS RainData')

# Create a table to store rain data with a column for rain detection and timestamp
cursor.execute('''
CREATE TABLE RainData (
    id INTEGER PRIMARY KEY,
    neighborhood TEXT,
    street TEXT,
    average_density REAL,
    rain_detected BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Fetch Neighborhood Data from the ArcGIS service
neighborhoods_url = 'https://services.arcgis.com/ZOyb2t4B0UYuYNYH/arcgis/rest/services/nma_nhoods_sub/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson'
neighborhoods_response = requests.get(neighborhoods_url)
neighborhoods_data = neighborhoods_response.json()

# Projection for converting coordinates from EPSG:2285 to WGS84
proj = pyproj.Transformer.from_crs("EPSG:2285", "EPSG:4326", always_xy=True)

# Function to check if a point is inside a polygon
def point_in_polygon(point, polygon):
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

# Function to determine neighborhood
def get_neighborhood(point):
    longitude, latitude = proj.transform(point[0], point[1])
    for feature in neighborhoods_data['features']:
        neighborhood = feature['properties']['S_HOOD']
        geometry = feature['geometry']
        
        if geometry['type'] == 'Polygon':
            polygons = [geometry['coordinates']]
        elif geometry['type'] == 'MultiPolygon':
            polygons = geometry['coordinates']
        else:
            continue
        
        for polygon in polygons:
            exterior_ring = polygon[0]  # Get the first ring of the polygon
            if not isinstance(exterior_ring[0][0], list):
                # Handle case where exterior_ring is not deeply nested
                exterior_ring = exterior_ring
            else:
                # Handle case where exterior_ring is deeply nested
                exterior_ring = exterior_ring[0]
            if point_in_polygon((longitude, latitude), exterior_ring):
                return neighborhood
    return 'Unknown'

# Improved function to extract street names from the URL and split them
def get_streets_from_url(url):
    match = re.search(r'images/([^_]+)_([^_]+)_([A-Za-z]+)', url)
    if match:
        streets = [match.group(1), match.group(2)]
        return streets
    return ['Unknown', 'Unknown']

# Fetch Traffic Camera Data
url = 'https://data-seattlecitygis.opendata.arcgis.com/api/download/v1/items/b90315ad1deb4985aeb3071b8baa06a1/geojson?layers=0'
response = requests.get(url)
data = response.json()

# Function to determine if it's raining and calculate edge density
def rain_density(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    # Calculate edge density
    edge_density = np.sum(edges) / (edges.shape[0] * edges.shape[1])
    return edge_density

# Dictionary to store rain densities by neighborhood and street
rain_data = {}

# Parse GeoJSON to get Camera URLs and Locations, and analyze each camera
for feature in data['features']:
    properties = feature['properties']
    camera_url = properties.get('URL', None)
    coordinates = feature['geometry']['coordinates']
    
    # Skip URLs that have only letters and numbers at the end and no underscores
    if camera_url and not re.search(r'/images/\w+$', camera_url):
        neighborhood = get_neighborhood(coordinates)
        streets = get_streets_from_url(camera_url)
        
        print(f'DEBUG: Original Coordinates: {coordinates}, Converted Coordinates: {proj.transform(coordinates[0], coordinates[1])}, Neighborhood: {neighborhood}, Streets: {streets}')  # Debug print
        
        try:
            image_resp = requests.get(camera_url, stream=True).raw
            image = np.asarray(bytearray(image_resp.read()), dtype="uint8")
            image = cv2.imdecode(image, cv2.IMREAD_COLOR)
            
            if image is not None:
                edge_density = rain_density(image)
                rain_detected = edge_density > 0.01  # Adjust threshold as needed
                if rain_detected:
                    print(f'Rain detected at camera in {neighborhood} at {streets[0]} and {streets[1]}: {camera_url}')
                    
                    # Add edge density to the neighborhood's data
                    if neighborhood not in rain_data:
                        rain_data[neighborhood] = {}
                    street_label = f"{streets[0]} and {streets[1]}"
                    if street_label not in rain_data[neighborhood]:
                        rain_data[neighborhood][street_label] = []
                    rain_data[neighborhood][street_label].append(edge_density)
        except Exception as e:
            print(f'Error processing camera in {neighborhood} at {streets[0]} and {streets[1]}: {e}')

# Calculate average rain density for each neighborhood and street and store in the database
for neighborhood, streets in rain_data.items():
    for street_label, densities in streets.items():
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if densities:
            average_density = np.mean(densities)
            print(f'Storing average rain density for {neighborhood} at {street_label}: {average_density}')  # Debug print
            cursor.execute('INSERT INTO RainData (neighborhood, street, average_density, rain_detected, timestamp) VALUES (?, ?, ?, ?, ?)', 
                           (neighborhood, street_label, average_density, True, timestamp))
        else:
            print(f'No rain data for {neighborhood} at {street_label}')
            cursor.execute('INSERT INTO RainData (neighborhood, street, average_density, rain_detected, timestamp) VALUES (?, ?, ?, ?, ?)', 
                           (neighborhood, street_label, 0, False, timestamp))

# Commit and close the database connection
conn.commit()
conn.close()
