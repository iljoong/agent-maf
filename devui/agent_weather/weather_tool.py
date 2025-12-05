import requests
from urllib.parse import quote
import json
import os
from typing import Annotated

# free http://wttr.in
def get_current_weather(
        city: Annotated[str, "The name of the city to fetch the weather for. The city must be in English, e.g., 'Seoul' or 'New York'."]
    ) -> str:
    """
    Fetches the current weather for a given city.

    :param city: The English name of the city to fetch the weather for.
    :return: A string describing the current weather in the city.
    """
    print(f"tool: getting current weather in \"{city}\"")

    city = quote(city)    
    url = f"http://wttr.in/{city}?format=j1"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            return f"Error fetching weather data"
        
        current_condition = data["current_condition"][0]
        weather = current_condition["weatherDesc"][0]["value"]
        temperature = current_condition["temp_C"]
        humidity = current_condition["humidity"]
        return f"The current weather in {city} is {weather} with a temperature of {temperature}°C and humidity of {humidity}%. "
    except Exception as e:
        return f"Error fetching weather data: {str(e)}"
    
if __name__ == "__main__":
    print(get_current_weather("seoul"))