from django import template
import json

register = template.Library()

@register.filter
def json_decode(value):
    return json.loads(value)

@register.filter(name='split')
def split(value, delimiter):
    return value.split(delimiter)

@register.filter
def trim(value):
    return value.strip()
# In weather_filters.py
@register.filter
@register.filter
def get_condition_code(report):
    """Maps textual weather conditions to OpenWeatherMap icon codes"""
    condition_mapping = {
        # Clear
        'clear sky': '01d',
        'sunny': '01d',

        # Clouds
        'few clouds': '02d',
        'scattered clouds': '03d',
        'broken clouds': '04d',
        'overcast clouds': '04d',
        'partly cloudy': '02d',

        # Rain
        'light rain': '10d',
        'moderate rain': '10d',
        'heavy rain': '09d',
        'shower rain': '09d',
        'rain showers': '09d',

        # Thunderstorm
        'thunderstorm': '11d',

        # Snow
        'snow': '13d',
        'light snow': '13d',
        'heavy snow': '13d',

        # Atmosphere
        'mist': '50d',
        'fog': '50d',
        'haze': '50d',
    }

    # Extract the condition text
    for line in report.splitlines():
        if line.startswith('Conditions:'):
            condition_text = line.split(':', 1)[1].strip().lower()
            # Find the best matching condition
            for key in condition_mapping:
                if key in condition_text:
                    return condition_mapping[key]

    return '01d'  # Default to clear sky

@register.filter
def get_condition_text(report):
    """Extracts just the condition text for display"""
    for line in report.splitlines():
        if line.startswith('Conditions:'):
            return line.split(':', 1)[1].strip()
    return "Unknown"


@register.filter
def get_temp_extremes(reports):
    min_temps = []
    max_temps = []

    for report in reports:
        try:
            # Extract from "Temperature: X°C" format
            temp_line = next(line for line in report['report'].splitlines()
                             if line.startswith('Temperature:'))
            temp = float(temp_line.split(':')[1].split('°')[0].strip())
            min_temps.append(temp - 2)  # Estimate min 2° below
            max_temps.append(temp + 2)  # Estimate max 2° above
        except:
            continue

    if not min_temps:
        return {'min': 'N/A', 'max': 'N/A'}

    return {
        'min': f"{min(min_temps):.1f}°C",
        'max': f"{max(max_temps):.1f}°C"
    }
@register.filter
def get_max_temp(reports):
    max_temp = -float('inf')
    for report in reports:
        for line in report['report'].splitlines():
            if "Temperature:" in line:
                temp = float(line.split(":")[1].strip().replace("°C", ""))
                if temp > max_temp:
                    max_temp = temp
    return float(max_temp) if max_temp != -float('inf') else "N/A"
@register.filter
def get_min_temp(reports):
    min_temp = float('inf')
    for report in reports:
        for line in report['report'].splitlines():
            if "Temperature:" in line:
                temp = float(line.split(":")[1].strip().replace("°C", ""))
                if temp < min_temp:
                    min_temp = temp
    return float(min_temp) if min_temp != float('inf') else "N/A"