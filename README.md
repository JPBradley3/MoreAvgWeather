# MoreAvgWeather

## Description
MoreAvgWeather is a web application that provides users with historical and average weather data for various locations. The project aims to deliver easy-to-understand weather trends and insights based on past weather patterns.

## Features
- **Search Historical Weather Data**: Retrieve average temperature, precipitation, and other weather metrics for specific locations.
- **Graphical Representations**: View weather trends using interactive charts.
- **Customizable Date Range**: Select different time periods to analyze historical weather data.
- **Responsive Design**: Optimized for both desktop and mobile devices.

## Installation
1. **Clone the Repository**:
   ```sh
   git clone https://github.com/JPBradley3/MoreAvgWeather.git
   ```

2. **Navigate to the Project Directory**:
   ```sh
   cd MoreAvgWeather
   ```

3. **Set Up a Virtual Environment** (optional but recommended):
   ```sh
   python3 -m venv env
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

4. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

5. **Set Up API Keys**:
   - Obtain an API key from a weather data provider (such as NOAA or OpenWeather).
   - Configure the API key in the environment variables or application settings.

## Usage
To run the application locally:

1. **Start the Application**:
   ```sh
   python app.py
   ```

2. **Access the Application**:
   Open a web browser and navigate to `http://localhost:5000` (or the specified port number) to use the application.

## Technologies Used
- **Programming Language**: Python
- **Libraries and Frameworks**:
  - **Flask**: Used for creating the web application.
  - **Requests**: Utilized for fetching weather data from APIs.
  - **Matplotlib / Plotly**: Used for generating graphical representations of weather trends.
  - **Pandas**: For data manipulation and analysis.

## License
*The repository does not specify a license. It's advisable to contact the repository owner for clarification before using or distributing the code.*

For more detailed information, please visit the [MoreAvgWeather GitHub repository](https://github.com/JPBradley3/MoreAvgWeather).
