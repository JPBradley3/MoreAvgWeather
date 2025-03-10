import schedule
import time
import subprocess
import logging
import sys

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def run_nws_scraper():
    result = subprocess.run(['python', 'scrape_nws.py'])
    logging.info('NWS scraper ran successfully' if result.returncode == 0 else f'NWS scraper failed with code {result.returncode}')

def run_openmeteo_scraper():
    result = subprocess.run(['python', 'scrape_openmeteo.py'])
    logging.info('Open-Meteo scraper ran successfully' if result.returncode == 0 else f'Open-Meteo scraper failed with code {result.returncode}')

def run_weatherapi_scraper():
    result = subprocess.run(['python', 'scrape_weatherapi.py'])
    logging.info('WeatherAPI scraper ran successfully' if result.returncode == 0 else f'WeatherAPI scraper failed with code {result.returncode}')

def run_weatherstack_scraper():
    result = subprocess.run(['python', 'scrape_weatherstack.py'])
    logging.info('WeatherStack scraper ran successfully' if result.returncode == 0 else f'WeatherStack scraper failed with code {result.returncode}')

def run_openweathermap_scraper():
    result = subprocess.run(['python', 'scrape_openweathermap.py'])
    logging.info('OpenWeatherMap scraper ran successfully' if result.returncode == 0 else f'OpenWeatherMap scraper failed with code {result.returncode}')

def clean_scrapers1():
    result = subprocess.run(['python', 'edit_with_altitude.py'])
    logging.info('Added altitude data successfully' if result.returncode == 0 else f'Altitude data script failed with code {result.returncode}')

def clean_scrapers2():
    result = subprocess.run(['python', 'edit_with_barometer.py'])
    logging.info('Added barometer calculation successfully' if result.returncode == 0 else f'Barometer calculation script failed with code {result.returncode}')

def apply_prediction1():
    result = subprocess.run(['python', 'basic_rain_prediction.py'])
    logging.info('Added rain prediction from Triple Point Observation successfully' if result.returncode == 0 else f'Rain prediction script failed with code {result.returncode}')

def run_all_processes():
    run_nws_scraper()
    run_openmeteo_scraper()
    run_weatherapi_scraper()
    run_openweathermap_scraper()
    clean_scrapers1()
    clean_scrapers2()
    apply_prediction1()

# Schedule the scripts to run every 15 minutes
schedule.every(15).minutes.do(run_nws_scraper)
schedule.every(15).minutes.do(run_openmeteo_scraper)
schedule.every(15).minutes.do(run_weatherapi_scraper)
schedule.every(15).minutes.do(run_openweathermap_scraper)
schedule.every(15).minutes.do(clean_scrapers1)
schedule.every(15).minutes.do(clean_scrapers2)
schedule.every(15).minutes.do(apply_prediction1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        run_all_processes()
    else:
        while True:
            schedule.run_pending()
            time.sleep(1)
