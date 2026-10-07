import requests

CITY_COORDS = {
    'Ahmedabad': {'lat': 23.0225, 'lon': 72.5714},
    'Bangalore': {'lat': 12.9716, 'lon': 77.5946},
    'Chennai':   {'lat': 13.0827, 'lon': 80.2707},
    'Delhi':     {'lat': 28.6139, 'lon': 77.2090},
    'Hyderabad': {'lat': 17.3850, 'lon': 78.4867},
    'Jaipur':    {'lat': 26.9124, 'lon': 75.7873},
    'Kolkata':   {'lat': 22.5726, 'lon': 88.3639},
    'Lucknow':   {'lat': 26.8467, 'lon': 80.9462},
    'Mumbai':    {'lat': 19.0760, 'lon': 72.8777},
    'Pune':      {'lat': 18.5204, 'lon': 73.8567}
}

def fetch_current_weather(city_name):
    """
    Fetches the current live weather for a given city using Open-Meteo API.
    Returns a dictionary of current values.
    """
    if city_name not in CITY_COORDS:
        raise ValueError(f"Coordinates for city '{city_name}' not found.")
        
    coords = CITY_COORDS[city_name]
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords['lat'],
        "longitude": coords['lon'],
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "wind_speed_10m"],
        "timezone": "auto"
    }
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch live data: {response.text}")
        
    data = response.json()
    current = data['current']
    
    return {
        'temperature': current['temperature_2m'],
        'humidity': current['relative_humidity_2m'],
        'apparent_temperature': current['apparent_temperature'],
        'precipitation': current['precipitation'],
        'wind_speed': current['wind_speed_10m'],
        'time': current['time']
    }
