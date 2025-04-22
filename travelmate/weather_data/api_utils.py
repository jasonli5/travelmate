import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import statistics
from collections import defaultdict

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("API key not found in environment variables")

# Constants
FORECAST_DAYS = 8  # Standard OpenWeatherMap forecast limit (8-1)
HISTORICAL_YEARS = 5  # Number of years to look back for aggregation data
MAX_FUTURE_DAYS = 365 * 1.5  # 1.5 years in future (practical limit)


def get_coordinates(location_name):
    """Get latitude and longitude from location name using Geocoding API"""
    # Clean the input - remove extra spaces and normalize formatting
    location_name = location_name.strip()

    # Try different query formats if initial attempt fails
    query_formats = [
        location_name,  # Try original input first
        f"{location_name}, US",  # Explicitly add country code
        location_name.replace(", ", ",")  # Try without space after comma
    ]

    for query in query_formats:
        geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={API_KEY}"
        response = requests.get(geocode_url)

        if response.status_code == 200 and response.json():
            data = response.json()
            break
    else:
        raise ValueError("Location not found after multiple attempts")

    # Find the best match among results
    best_match = None
    location_parts = [part.strip().lower() for part in location_name.split(",")]

    for location in data:
        # Check if state matches (for US locations)
        if len(location_parts) > 1 and location.get('country') == 'US':
            state_abbr = location_parts[1].upper()
            state_name = location.get('state', '').upper()

            # Match state abbreviation or full name
            if (state_abbr == state_name or
                    (len(state_abbr) == 2 and state_name.startswith(state_abbr))):
                best_match = location
                break

        # Match city name
        if location.get('name', '').lower() == location_parts[0].lower():
            best_match = location
            break

    # Fallback to first result if no perfect match found
    if not best_match and data:
        best_match = data[0]

    if not best_match:
        raise ValueError("Location not found in API response")

    # Format the location name nicely
    name_parts = [best_match.get('name', '')]
    if best_match.get('state'):
        name_parts.append(best_match['state'])
    else:
        name_parts.append(best_match.get('country', ''))

    return {
        'lat': best_match['lat'],
        'lon': best_match['lon'],
        'name': ', '.join(name_parts)
    }


def get_weather_data(lat, lon, target_date=None):
    """
    Get weather data using One Call API 3.0
    - For current+forecast: leave target_date=None
    - For specific date: provide target_date as datetime object
    """
    now = datetime.now()

    if target_date:
        if target_date > now + timedelta(days=MAX_FUTURE_DAYS):
            raise ValueError(f"Forecast data only available up to {MAX_FUTURE_DAYS} days in the future")

        if target_date.date() == now.date():
            # Current weather
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={API_KEY}"
            response = requests.get(url)
            return {'current': response.json()['current']}
        elif now < target_date <= (now + timedelta(days=FORECAST_DAYS)):
            # Future forecast within standard forecast window
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={API_KEY}"
            response = requests.get(url)
            for day in response.json()['daily']:
                day_date = datetime.fromtimestamp(day['dt'])
                if day_date.date() == target_date.date():
                    return day
            raise ValueError("Date not found in forecast data")
        elif target_date > now:
            # Beyond forecast window - use historical aggregation
            return get_historical_aggregation(lat, lon, target_date)
        else:
            # Historical data
            timestamp = int(target_date.timestamp())
            url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&units=metric&appid={API_KEY}"
            response = requests.get(url)
            return {'current': response.json()['data'][0]}  # Historical returns array in 'data' field
    else:
        # Current weather and forecast
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={API_KEY}"
        response = requests.get(url)
        return response.json()


def get_historical_aggregation(lat, lon, target_date):
    """
    Get aggregated historical weather data for the same date in previous years
    to predict weather beyond the forecast window.
    """
    now = datetime.now()
    if target_date <= now:
        raise ValueError("Target date must be in the future for aggregation prediction")

    # Calculate target day of year
    target_day = target_date.timetuple().tm_yday

    historical_data = defaultdict(list)
    weather_codes = []

    # Get data for the same date in previous years
    for year_offset in range(1, HISTORICAL_YEARS + 1):
        historical_date = target_date - timedelta(days=365 * year_offset)

        try:
            # Get historical weather for this date
            timestamp = int(historical_date.timestamp())
            url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&units=metric&appid={API_KEY}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()['data'][0]

                # Collect all numerical data
                for key in ['temp', 'feels_like', 'pressure', 'humidity', 'dew_point',
                            'clouds', 'wind_speed', 'wind_deg']:
                    if key in data:
                        historical_data[key].append(data[key])

                # Collect weather conditions
                if 'weather' in data and len(data['weather']) > 0:
                    weather_codes.append(data['weather'][0]['id'])
        except Exception as e:
            print(f"Warning: Couldn't get historical data for {historical_date}: {str(e)}")
            continue

    if not historical_data:
        raise ValueError("No historical data available for prediction")

    # Calculate averages for numerical data
    aggregated = {
        'dt': int(target_date.timestamp()),
        'temp': statistics.mean(historical_data['temp']),
        'feels_like': statistics.mean(historical_data['feels_like']),
        'pressure': round(statistics.mean(historical_data['pressure'])),
        'humidity': round(statistics.mean(historical_data['humidity'])),
        'dew_point': statistics.mean(historical_data['dew_point']),
        'clouds': round(statistics.mean(historical_data['clouds'])),
        'wind_speed': round(statistics.mean(historical_data['wind_speed'])),
        'wind_deg': round(statistics.mean(historical_data['wind_deg'])),
    }

    # Determine most likely weather condition
    if weather_codes:
        # Group weather codes into broader categories
        weather_categories = defaultdict(int)
        for code in weather_codes:
            category = code // 100  # First digit indicates general weather type
        weather_categories[category] += 1

        # Get most common category
        most_common = max(weather_categories.items(), key=lambda x: x[1])[0]

        # Map to a representative weather code in that category
        representative_code = {
            2: 200,  # Thunderstorm
            3: 300,  # Drizzle
            5: 500,  # Rain
            6: 600,  # Snow
            7: 701,  # Atmosphere (mist, fog, etc.)
            8: 800 if most_common == 8 else 801  # Clear or few clouds
            }.get(most_common, 800)

        aggregated['weather'] = [{
            'id': representative_code,
            'main': get_weather_main(representative_code),
            'description': get_weather_description(representative_code),
            'icon': get_weather_icon(representative_code)
        }]
    else:
        # Default to fair weather if no historical data
        aggregated['weather'] = [{
            'id': 800,
            'main': 'Clear',
            'description': 'clear sky',
            'icon': '01d'
            }]

    # Add sunrise/sunset estimates (not available in historical API)
    aggregated['sunrise'] = int((target_date.replace(hour=6, minute=0, second=0)).timestamp())
    aggregated['sunset'] = int((target_date.replace(hour=18, minute=0, second=0)).timestamp())

    return aggregated


def get_weather_main(code):
    """Map weather code to main category"""
    weather_map = {
        200: 'Thunderstorm',
        300: 'Drizzle',
        500: 'Rain',
        600: 'Snow',
        701: 'Mist',
        711: 'Smoke',
        721: 'Haze',
        731: 'Dust',
        741: 'Fog',
        751: 'Sand',
        761: 'Dust',
        762: 'Ash',
        771: 'Squall',
        781: 'Tornado',
        800: 'Clear',
        801: 'Clouds',
        802: 'Clouds',
        803: 'Clouds',
        804: 'Clouds'
    }
    return weather_map.get(code, 'Clear')


def get_weather_description(code):
    """Map weather code to description"""
    weather_map = {
        200: 'thunderstorm with light rain',
        300: 'light intensity drizzle',
        500: 'light rain',
        600: 'light snow',
        701: 'mist',
        711: 'smoke',
        721: 'haze',
        731: 'dust whirls',
        741: 'fog',
        751: 'sand',
        761: 'dust',
        762: 'volcanic ash',
        771: 'squalls',
        781: 'tornado',
        800: 'clear sky',
        801: 'few clouds',
        802: 'scattered clouds',
        803: 'broken clouds',
        804: 'overcast clouds'
    }
    return weather_map.get(code, 'clear sky')


def get_weather_icon(code):
    """Map weather code to icon"""
    weather_map = {
        200: '11d',
        300: '09d',
        500: '10d',
        600: '13d',
        701: '50d',
        711: '50d',
        721: '50d',
        731: '50d',
        741: '50d',
        751: '50d',
        761: '50d',
        762: '50d',
        771: '50d',
        781: '50d',
        800: '01d',
        801: '02d',
        802: '03d',
        803: '04d',
        804: '04d'
    }
    return weather_map.get(code, '01d')


def format_weather_output(weather_data, location_name, is_prediction=False):
    """Format weather data for nice display"""
    if 'current' in weather_data:  # Current or historical data
        data = weather_data['current']
        output_date = datetime.fromtimestamp(data['dt']).strftime('%a, %b %d %Y')
    else:  # Daily forecast data
        data = weather_data
        output_date = datetime.fromtimestamp(data['dt']).strftime('%a, %b %d %Y')

    # Handle different temperature structures
    if 'temp' in data and isinstance(data['temp'], dict):
        temp = data['temp']['day']
        feels_like = data['feels_like']['day']
    else:
        temp = data.get('temp', 'N/A')
        feels_like = data.get('feels_like', 'N/A')

    prediction_note = "\nNote: This is a prediction based on historical weather patterns" if is_prediction else ""

    return f"""
Weather for {location_name}
{output_date}
--------------------
Temperature: {temp}°C
Feels like: {feels_like}°C
Conditions: {data['weather'][0]['description'].title()}
Humidity: {data.get('humidity', 'N/A')}%
Pressure: {data.get('pressure', 'N/A')} hPa
Wind: {data.get('wind_speed', 'N/A')} m/s, {data.get('wind_deg', 'N/A')}°
Clouds: {data.get('clouds', 'N/A')}%
{'' if 'sunrise' not in data else f"Sunrise: {datetime.fromtimestamp(data['sunrise']).strftime('%H:%M')}"}
{'' if 'sunset' not in data else f"Sunset: {datetime.fromtimestamp(data['sunset']).strftime('%H:%M')}"}
{prediction_note}
"""


def get_date_range_weather(lat, lon, location_name, start_date, end_date):
    """Get weather for a range of dates"""
    results = []
    current_date = start_date
    now = datetime.now()

    # First try to get all data from forecast if possible
    if start_date > now and end_date <= now + timedelta(days=FORECAST_DAYS):
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={API_KEY}"
        response = requests.get(url)
        forecast_data = response.json()

        for day in forecast_data['daily']:
            day_date = datetime.fromtimestamp(day['dt'])
            if start_date <= day_date <= end_date:
                results.append(format_weather_output(day, location_name))

        return results

    # Otherwise go day by day
    while current_date <= end_date:
        try:
            if current_date > now + timedelta(days=FORECAST_DAYS):
                # Beyond forecast window - use historical aggregation
                weather = get_historical_aggregation(lat, lon, current_date)
                results.append(format_weather_output(weather, location_name, is_prediction=True))
            else:
                # Within forecast window or historical data
                weather = get_weather_data(lat, lon, current_date)
                results.append(format_weather_output(weather, location_name))
        except Exception as e:
            results.append(f"\nError getting data for {current_date.strftime('%Y-%m-%d')}: {str(e)}")

        current_date += timedelta(days=1)

    return results


def main():
    try:
        # Get location input
        location = input("Enter location (e.g., 'Paris' or 'Tokyo,JP'): ")
        coords = get_coordinates(location)
        location_name = coords['name']
        print(f"\nGetting weather for {location_name} (Lat: {coords['lat']}, Lon: {coords['lon']})")

        # Get date range input
        date_input = input("Enter date or range (YYYY-MM-DD or YYYY-MM-DD:YYYY-MM-DD): ").strip()

        if ":" in date_input:
            start_str, end_str = date_input.split(":")
            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")

            # Check if range is valid
            if end_date < start_date:
                raise ValueError("End date must be after start date")

            # Check if range is too large (API limits)
            if (end_date - start_date).days > 30:
                print("Warning: Large date range may take a while to process and make many API calls")

            # Get weather for range
            weather_reports = get_date_range_weather(
                coords['lat'],
                coords['lon'],
                location_name,
                start_date,
                end_date
            )

            # Print results
            print("\n" + "=" * 50)
            for report in weather_reports:
                print(report)
                print("-" * 50)
            print("=" * 50)

        else:
            # Single date request
            target_date = datetime.strptime(date_input, "%Y-%m-%d")
            now = datetime.now()

            if target_date > now + timedelta(days=FORECAST_DAYS):
                # Beyond forecast window - use historical aggregation
                weather = get_historical_aggregation(coords['lat'], coords['lon'], target_date)
                print(format_weather_output(weather, location_name, is_prediction=True))
            else:
                # Within forecast window or historical data
                weather = get_weather_data(coords['lat'], coords['lon'], target_date)
                print(format_weather_output(weather, location_name))

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please check your inputs and try again.")


if __name__ == "__main__":
    main()