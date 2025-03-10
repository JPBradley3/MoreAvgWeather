import sqlite3
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
import logging
import sys

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Connect to the SQLite database
conn = sqlite3.connect('weather_data.db')
cursor = conn.cursor()

# Check if the precipitation column exists and add it if not
cursor.execute("PRAGMA table_info(weather_data)")
columns = [column_info[1] for column_info in cursor.fetchall()]
if 'precipitation' not in columns:
    cursor.execute("ALTER TABLE weather_data ADD COLUMN precipitation REAL")
    conn.commit()

# Query the data from the database, including the id column
query = """
SELECT id, barometric_pressure, temperature, wind_speed, humidity
FROM weather_data
"""
df = pd.read_sql_query(query, conn)

# Ensure temperature column contains only string values
df['temperature'] = df['temperature'].astype(str)

# Replace non-numeric temperature values with NaN
df['temperature'] = df['temperature'].str.replace('°F', '', regex=False)
df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')

# Clean wind speed data by removing non-numeric characters and converting to numeric
df['wind_speed'] = df['wind_speed'].astype(str).str.extract('(\d+)')
df['wind_speed'] = pd.to_numeric(df['wind_speed'], errors='coerce')

# Clean humidity data by removing '%' and converting to numeric
df['humidity'] = df['humidity'].astype(str).str.replace('%', '', regex=False)
df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')

# Log the DataFrame to check for missing values
logging.info("DataFrame before handling missing values:")
logging.info(df.head())

# Define the features
X = df[['barometric_pressure', 'temperature', 'wind_speed', 'humidity']]

# Log the shape of the data
logging.info(f'Data shape before imputation: {X.shape}')

# Check for missing values
missing_values = X.isnull().sum()
logging.info(f'Missing values in each column:\n{missing_values}')

# Impute missing values with the mean
imputer = SimpleImputer(strategy='mean')
X = imputer.fit_transform(X)

# Log the shape of the data after imputation
logging.info(f'Data shape after imputation: {X.shape}')

# Check if the data has at least one feature
if X.shape[1] == 0:
    logging.error('Input data has zero features.')
    conn.close()
    sys.exit(1)

# Scale the features
scaler = StandardScaler()
try:
    X = scaler.fit_transform(X)
except ValueError as e:
    logging.error(f'Error scaling data: {e}')
    conn.close()
    sys.exit(1)

# Generate sample precipitation values (replace with actual data or prediction logic)
# For demonstration purposes, I'm using a simple threshold for example
y = (df['barometric_pressure'] < 1010).astype(int)  # Example: 1 if pressure < 1010, else 0

# Create and train the logistic regression model with increased iterations
model = LogisticRegression(max_iter=1000)
try:
    model.fit(X, y)
except ValueError as e:
    logging.error(f'Error fitting model: {e}')
    conn.close()
    sys.exit(1)

# Add precipitation predictions (probability) to the DataFrame
df['precipitation_probability'] = model.predict_proba(X)[:, 1]

# Convert probability to percentage
df['precipitation_percentage'] = df['precipitation_probability'] * 100

# Print the DataFrame to debug
logging.info("DataFrame before updating the database:")
logging.info(df.head())

# Define a function to update the precipitation data in the database using the id column
def update_precipitation_in_db():
    for index, row in df.iterrows():
        cursor.execute("""
        UPDATE weather_data
        SET precipitation = ?
        WHERE id = ?
        """, (row['precipitation_percentage'], row['id']))
    conn.commit()

# Update the precipitation data in the database
update_precipitation_in_db()

# Fetch and print the updated data for verification
updated_df = pd.read_sql_query("SELECT * FROM weather_data LIMIT 5", conn)
logging.info("DataFrame after updating the database:")
logging.info(updated_df)

# Close the database connection
conn.close()

logging.info("Precipitation data updated in the database.")
