#mocked

from datetime import datetime

def get_mock_weather():
    return {
        "temperature_celsius": 22.5,
        "condition": "Ensolarado",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_mock_weather_scenario(scenario="sunny"):
    if scenario == "rainy":
        return {
            "temperature_celsius": 16,
            "condition": "Chuvoso",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    elif scenario == "cloudy":
        return {
            "temperature_celsius": 20,
            "condition": "Nublado",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    else:  # default sunny
        return {
            "temperature_celsius": 22.5,
            "condition": "Ensolarado",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
