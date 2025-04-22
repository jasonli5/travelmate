import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("API key not found in environment variables")


def get_coordinates(location_name):
    """Get latitude and longitude from location name using Geocoding API"""
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location_name}&limit=1&appid={API_KEY}"

    response = requests.get(geocode_url)
    if response.status_code != 200:
        raise Exception(f"Geocoding API error: {response.status_code}")

    data = response.json()
    if not data:
        raise ValueError("Location not found")

    return {
        'lat': data[0]['lat'],
        'lon': data[0]['lon'],
        'name': f"{data[0].get('name', '')}, {data[0].get('country', '')}"
    }


def get_weather_data(lat, lon, target_date=None):
    """
    Get weather data using One Call API 3.0
    - For current+forecast: leave target_date=None
    - For historical: provide target_date as datetime object
    """
    if target_date:
        # Historical data call
        if target_date > datetime.now():
            raise ValueError("Historical data only available for past dates")

        timestamp = int(target_date.timestamp())
        url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&units=metric&appid={API_KEY}"
    else:
        # Forecast data call
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={API_KEY}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API error {response.status_code}: {response.text}")

    return response.json()


def format_weather_output(weather_data, date=None):
    """Format weather data for nice display"""
    if 'current' in weather_data:  # Historical or current data
        data = weather_data['current']
        output_date = datetime.fromtimestamp(data['dt']).strftime('%a, %b %d %Y')
    else:  # Daily forecast data
        data = weather_data
        output_date = datetime.fromtimestamp(data['dt']).strftime('%a, %b %d %Y')

    return f"""
{output_date}
--------------------
Temperature: {data.get('temp', data.get('temp', {}).get('day', 'N/A'))}°C
Feels like: {data.get('feels_like', data.get('feels_like', {}).get('day', 'N/A'))}°C
Conditions: {data['weather'][0]['description'].title()}
Humidity: {data.get('humidity', 'N/A')}%
Wind: {data.get('wind_speed', 'N/A')} m/s, {data.get('wind_deg', 'N/A')}°
Sunrise: {datetime.fromtimestamp(data.get('sunrise', 0)).strftime('%H:%M') if 'sunrise' in data else 'N/A'}
Sunset: {datetime.fromtimestamp(data.get('sunset', 0)).strftime('%H:%M') if 'sunset' in data else 'N/A'}
"""


def main():
    try:
        # Get location input
        location = input("Enter location (e.g., 'Paris' or 'Tokyo,JP'): ")
        coords = get_coordinates(location)
        print(f"\nGetting weather for {coords['name']} (Lat: {coords['lat']}, Lon: {coords['lon']})")

        # Get date range input
        date_input = input("Enter date or range (YYYY-MM-DD or YYYY-MM-DD:YYYY-MM-DD): ")

        if ":" in date_input:
            start_str, end_str = date_input.split(":")
            start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
            end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")

            # Check if range is valid
            if end_date < start_date:
                raise ValueError("End date must be after start date")

            current_date = start_date
            while current_date <= end_date:
                if current_date.date() == datetime.now().date():
                    # Today's weather
                    weather = get_weather_data(coords['lat'], coords['lon'])
                    print(format_weather_output(weather))
                elif current_date > datetime.now():
                    # Future date (use daily forecast)
                    weather = get_weather_data(coords['lat'], coords['lon'])
                    for day in weather['daily']:
                        day_date = datetime.fromtimestamp(day['dt'])
                        if day_date.date() == current_date.date():
                            print(format_weather_output(day))
                            break
                else:
                    # Historical data
                    weather = get_weather_data(coords['lat'], coords['lon'], current_date)
                    print(format_weather_output(weather))

                current_date += timedelta(days=1)
        else:
            # Single date request
            target_date = datetime.strptime(date_input.strip(), "%Y-%m-%d")
            if target_date.date() == datetime.now().date():
                weather = get_weather_data(coords['lat'], coords['lon'])
                print(format_weather_output(weather))
            elif target_date > datetime.now():
                weather = get_weather_data(coords['lat'], coords['lon'])
                for day in weather['daily']:
                    day_date = datetime.fromtimestamp(day['dt'])
                    if day_date.date() == target_date.date():
                        print(format_weather_output(day))
                        break
            else:
                weather = get_weather_data(coords['lat'], coords['lon'], target_date)
                print(format_weather_output(weather))

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please check your inputs and try again.")


if __name__ == "__main__":
    main()