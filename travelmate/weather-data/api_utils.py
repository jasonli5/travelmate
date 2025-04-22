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
    - For specific date: provide target_date as datetime object
    """
    now = datetime.now()

    if target_date:
        # Check if date is within forecast range (up to 1.5 years in future)
        max_forecast_date = now + timedelta(days=547)  # ~1.5 years

        if target_date > max_forecast_date:
            raise ValueError("Forecast data only available up to 1.5 years in the future")

        if target_date.date() == now.date():
            # Current weather
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={API_KEY}"
            response = requests.get(url)
            return {'current': response.json()['current']}
        elif target_date > now:
            # Future forecast (daily)
            url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={API_KEY}"
            response = requests.get(url)
            for day in response.json()['daily']:
                day_date = datetime.fromtimestamp(day['dt'])
                if day_date.date() == target_date.date():
                    return day
            raise ValueError("Date not found in forecast data")
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


def format_weather_output(weather_data, location_name):
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
"""


def get_date_range_weather(lat, lon, location_name, start_date, end_date):
    """Get weather for a range of dates"""
    results = []
    current_date = start_date
    now = datetime.now()

    # First try to get all data from forecast if possible
    if start_date > now:
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
            weather = get_weather_data(coords['lat'], coords['lon'], target_date)
            print(format_weather_output(weather, location_name))

    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please check your inputs and try again.")


if __name__ == "__main__":
    main()