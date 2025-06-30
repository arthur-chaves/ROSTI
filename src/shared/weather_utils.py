import os
import requests

def get_current_conditions(api_key, latitude, longitude):
    url = (
        f"https://weather.googleapis.com/v1/currentConditions:lookup"
        f"?key={api_key}"
        f"&location.latitude={latitude}"
        f"&location.longitude={longitude}"
    )
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        raise Exception(f"Erro na API: {data.get('error', 'Erro desconhecido')}")

    temperature = data['temperature']['degrees']
    description = data['weatherCondition']['description']['text']
    icon_url = data['weatherCondition']['iconBaseUri']

    return {
        "temperature": temperature,
        "description": description,
        "icon_url": icon_url,
        "current_time": data['currentTime'],
        "time_zone": data['timeZone']['id']
    }



def get_daily_forecast(api_key, latitude, longitude):
    url = (
        f"https://weather.googleapis.com/v1/forecast/days:lookup"
        f"?key={api_key}"
        f"&location.latitude={latitude}"
        f"&location.longitude={longitude}"
        f"&days=1"
    )
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        raise Exception(f"Erro na API: {data.get('error', 'Erro desconhecido')}")

    day_forecast = data['forecastDays'][0]

    daytime = day_forecast['daytimeForecast']
    nighttime = day_forecast['nighttimeForecast']

    max_temp = day_forecast['maxTemperature']['degrees']
    min_temp = day_forecast['minTemperature']['degrees']

    day_desc = daytime['weatherCondition']['description']['text']
    day_icon = daytime['weatherCondition']['iconBaseUri']

    night_desc = nighttime['weatherCondition']['description']['text']
    night_icon = nighttime['weatherCondition']['iconBaseUri']

    date_info = day_forecast['displayDate']
    date_str = f"{date_info['year']}-{date_info['month']:02d}-{date_info['day']:02d}"

    timezone = data.get('timeZone', {}).get('id', '')

    return {
        "date": date_str,
        "timezone": timezone,
        "max_temp": max_temp,
        "min_temp": min_temp,
        "day_desc": day_desc,
        "day_icon": day_icon,
        "night_desc": night_desc,
        "night_icon": night_icon,
    }

