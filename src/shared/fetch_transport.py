import requests
from dotenv import load_dotenv
import sys
import os
import time
import json
from datetime import datetime, timedelta
from app.utils.db_utils import get_connection

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

VEHICLE_TYPE_MAP = {
    "BUS": "bus",
    "RAIL": "train",
    "HEAVY_RAIL": "train",
    "COMMUTER_TRAIN": "train",
    "SUBWAY": "subway",
    "TRAM": "tram",
    "FERRY": "ferry",
    "CABLE_CAR": "cable car",
    "GONDOLA_LIFT": "gondola lift",
    "FUNICULAR": "funicular",
}

def get_swim_spots():
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT name FROM swim_spots;")
            return [row[0] for row in cur.fetchall()]

def get_transport_data(origin: str, destination: str, departure_time="now"):
    """
    Requests detailed public transit route from origin to destination,
    with a fallback if 'bus' mode returns no results.

    Args:
        origin (str): address or "lat,lng" coordinates of origin
        destination (str): address or "lat,lng" coordinates of destination
        departure_time (str or int): 'now' or unix timestamp of departure time

    Returns:
        dict: Directions API response data
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"

    if departure_time == "now":
        # Replace 'now' with current timestamp for more control
        departure_time = int(time.time())

    modes_to_try = ["bus", None]  # try with 'bus', then with all transit modes
    for transit_mode in modes_to_try:
        params = {
            "origin": origin,
            "destination": destination,
            "mode": "transit",
            "departure_time": departure_time,
            "key": API_KEY,
            "language": "en-US",
            "alternatives": "true"
        }
        if transit_mode:
            params["transit_mode"] = transit_mode

        response = requests.get(url, params=params)
        print(f"[DEBUG] Params used: {params}")
        data = response.json()
        print("[DEBUG] API response:", data)

        if response.status_code != 200:
            raise Exception(f"HTTP request error: {response.status_code}")

        if data.get("status") == "OK":
            return data
        else:
            print(f"[WARNING] Attempt with transit_mode={transit_mode} failed: {data.get('status')}")

    raise Exception("No valid route found by the Directions API.")


def parse_transport_response(data):
    """
    Extracts detailed transit route information (line, stop, time).

    Args:
        data (dict): JSON returned by the Directions API

    Returns:
        str: formatted message with trip information or error
    """
    try:
        routes = data.get("routes", [])
        if not routes:
            return "No routes found."

        steps = routes[0].get("legs", [])[0].get("steps", [])
        if not steps:
            return "No steps found in the route."

        for step in steps:
            if step.get("travel_mode") == "TRANSIT":
                details = step.get("transit_details", {})
                line = details.get("line", {}).get("short_name", "N/A")
                departure_stop = details.get("departure_stop", {}).get("name", "N/A")
                departure_time = details.get("departure_time", {}).get("text", "N/A")
                arrival_stop = details.get("arrival_stop", {}).get("name", "N/A")
                arrival_time = details.get("arrival_time", {}).get("text", "N/A")
                duration = routes[0]["legs"][0].get("duration", {}).get("text", "N/A")
                distance = routes[0]["legs"][0].get("distance", {}).get("text", "N/A")

                vehicle_raw = details.get("line", {}).get("vehicle", {}).get("type", "")
                vehicle = VEHICLE_TYPE_MAP.get(vehicle_raw, "public transport")
                return (
                    f"Take the {vehicle} {line} from '{departure_stop}' at {departure_time}.\n"
                    f"You will arrive at '{arrival_stop}' at {arrival_time}.\n"
                    f"Total duration: {duration} ({distance})."
                )

        return "Could not find a transit step in the route."
    except Exception as e:
        return f"Error processing transit data: {e}"


def insert_transport(origin, destination, duration_minutes):
    """
    Inserts transport data into the database.

    Args:
        origin (str)
        destination (str)
        duration_minutes (int)
    """
    con = get_connection()
    try:
        with con:
            with con.cursor() as cur:
                cur.execute("""
                    INSERT INTO transport_raw (origin, destination, duration_minutes)
                    VALUES (%s, %s, %s)
                """, (origin, destination, duration_minutes))
    finally:
        con.close()


def load_mock_response(file_path="mock_transport.json"):
    """
    Loads a mock API response for local/offline testing.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    ORIGIN = os.getenv("USER_CITY")

    # Set to True to use local mock data for testing
    USE_MOCK = False

    swim_spots = get_swim_spots()

    for spot in swim_spots:
        try:
            print(f"\n🏝️ Destination: {spot}")
            if USE_MOCK:
                data = load_mock_response()
            else:
                # Example: next Tuesday at 9 AM
                next_tuesday = datetime.now() + timedelta((1 - datetime.now().weekday()) % 7)
                fixed_time = datetime.combine(next_tuesday, datetime.strptime("09:00", "%H:%M").time())
                departure_timestamp = int(fixed_time.timestamp())

                data = get_transport_data(ORIGIN, spot, departure_time=departure_timestamp)

            message = parse_transport_response(data)
            print(message)
        except Exception as e:
            print(f"❌ Error processing {spot}: {e}")


def simplify_directions_response(data):
    if data.get("status") != "OK":
        return {"status": data.get("status"), "error_message": data.get("error_message")}

    simplified_routes = []
    for route in data.get("routes", []):
        simplified_legs = []
        for leg in route.get("legs", []):
            simplified_steps = []
            for step in leg.get("steps", []):
                step_info = {
                    "travel_mode": step.get("travel_mode"),
                    "instruction": step.get("html_instructions"),
                    "duration": step.get("duration", {}).get("text"),
                    "distance": step.get("distance", {}).get("text"),
                }
                if step.get("travel_mode") == "TRANSIT":
                    transit = step.get("transit_details", {})
                    step_info["transit"] = {
                        "line": transit.get("line", {}).get("short_name"),
                        "vehicle_type": transit.get("line", {}).get("vehicle", {}).get("type"),
                        "departure_stop": transit.get("departure_stop", {}).get("name"),
                        "arrival_stop": transit.get("arrival_stop", {}).get("name"),
                        "departure_time": transit.get("departure_time", {}).get("text"),
                        "arrival_time": transit.get("arrival_time", {}).get("text"),
                    }
                simplified_steps.append(step_info)
            simplified_legs.append({
                "start_address": leg.get("start_address"),
                "end_address": leg.get("end_address"),
                "duration": leg.get("duration", {}).get("text"),
                "distance": leg.get("distance", {}).get("text"),
                "steps": simplified_steps,
            })
        simplified_routes.append({
            "summary": route.get("summary"),
            "legs": simplified_legs,
        })
    return {
        "status": data.get("status"),
        "routes": simplified_routes,
    }

def generate_transport_summary(data):
    """
    Generates a simple message with essential route info: transit + walking + destination.
    """
    try:
        leg = data["routes"][0]["legs"][0]
        steps = leg["steps"]

        line_name = None
        vehicle_type = None
        departure_stop = None
        departure_time = None
        walking_duration = 0

        for step in steps:
            if step["travel_mode"] == "TRANSIT":
                transit = step["transit_details"]
                line_name = transit["line"]["short_name"]
                vehicle_raw = transit["line"]["vehicle"]["type"]
                vehicle_type = VEHICLE_TYPE_MAP.get(vehicle_raw, "public transport")
                departure_stop = transit["departure_stop"]["name"]
                departure_time = transit["departure_time"]["text"]
            elif step["travel_mode"] == "WALKING":
                walking_duration += step["duration"]["value"]  # in seconds

        walking_minutes = walking_duration // 60
        destination = leg.get("end_address", "your destination")

        if line_name and departure_stop and departure_time:
            return (
                f"Take the {vehicle_type} {line_name} from '{departure_stop}' at {departure_time}.\n"
                f"Then walk about {walking_minutes} minutes to reach {destination}."
            )
        else:
            return "No valid transit information found in the route."

    except Exception as e:
        return f"Error while generating route summary: {e}"


import urllib.parse

def generate_maps_link(origin, destination, departure_time=None):
    base_url = "https://www.google.com/maps/dir/?api=1"
    params = {
        "origin": origin,
        "destination": destination,
        "travelmode": "transit",
    }
    if departure_time:
        params["departure_time"] = str(departure_time)

    query = "&".join(f"{k}={urllib.parse.quote_plus(v)}" for k, v in params.items())
    return f"{base_url}&{query}"
