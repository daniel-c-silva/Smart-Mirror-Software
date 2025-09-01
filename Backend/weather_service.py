# weather_service.py
import requests

# ! Configuration (You can move these to a config file later)
OPENWEATHER_API_KEY = "your own api"  # * Get from https://openweathermap.org/api
CITY = "Porto"

# ! Function to get weather data from API
def get_weather_data():
    """
    Fetches current weather data from OpenWeatherMap API.
    Returns a dictionary with temperature, description, and city.
    Returns None if there's an error.
    """
    try:
        # * Build API URL with city and API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
        
        # * Make request to weather API
        response = requests.get(url)
        response.raise_for_status()  # * Raises exception for HTTP errors (4xx, 5xx)
        
        data = response.json()
        
        # * Extract and return relevant weather data
        return {
            "weather": {
                "location": data['name'],
                "tempC": round(data['main']['temp']),
                "condition": data['weather'][0]['description'],
                "humidity": data['main']['humidity'],
                "windSpeed": data['wind']['speed']
            }
        }
    except requests.exceptions.RequestException as e:
        print(f"[Weather Service] API Request Failed: {e}")
        return {"weather": None, "error": "API request failed"}
    except KeyError as e:
        print(f"[Weather Service] Error parsing weather data: {e}")
        return {"weather": None, "error": "Invalid response format"}
    except Exception as e:
        print(f"[Weather Service] Unexpected error: {e}")
        return {"weather": None, "error": "Unexpected error"}


# ! Test the function if run directly
if __name__ == "__main__":
    weather = get_weather_data()
    if weather and weather.get("weather"):
        w = weather["weather"]
        print(f"Weather in {w['location']}: {w['tempC']}°C, {w['condition']}")
    else:
        print("Failed to get weather data.")
