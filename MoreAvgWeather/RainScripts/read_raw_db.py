import sqlite3
from prettytable import PrettyTable

def read_weather_data(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query to select all data from the weather_data table
    cursor.execute('SELECT * FROM weather_data')

    # Fetch all rows from the query result
    rows = cursor.fetchall()

    # Create a PrettyTable object
    table = PrettyTable()

    # Get column names and set them as table field names
    column_names = [description[0] for description in cursor.description]
    table.field_names = column_names

    # Add rows to the table
    for row in rows:
        table.add_row(row)

    # Print the table
    print(table)

    # Close the connection
    conn.close()

db_name = 'weather_data.db'
read_weather_data(db_name)
