def generate_checklist(forecast_data):
    max_temp = forecast_data.get("max_temp", 22)
    min_temp = forecast_data.get("min_temp", 16)
    day_desc = forecast_data.get("day_desc", "").lower()
    night_desc = forecast_data.get("night_desc", "").lower()

    checklist = []
    message = ""

    # Rain or storm condition
    if "rain" in day_desc or "storm" in day_desc:
        checklist = ["Umbrella", "Book", "Power bank", "Extra socks"]
        message = "🌧️ Looks like it’s going to rain! Bring something to stay dry and entertained."

    # Clear and hot day
    elif "clear" in day_desc and max_temp >= 25:
        checklist = [
            "Sunscreen", "Sunglasses", "Hat", "Snorkel", "Towel",
            "Water bottle", "Power bank", "Shopping bag",
            "Running shoes", "Fruit", "Offline map"
        ]
        message = "☀️ Perfect day to swim or relax outdoors. Don’t forget your sunscreen!"

    # Cloudy weather
    elif "cloud" in day_desc:
        checklist = ["Light backpack", "Comfortable shoes", "Light jacket", "Book", "Water bottle", "Snacks"]
        message = "⛅ Cloudy day... Ideal for a calm walk or city exploration."

    else:
        checklist = ["Backpack", "Water bottle", "Offline map", "Snacks"]
        message = "📦 Be ready for anything! Neutral weather can still surprise you."


    # Add if night is cold
    if min_temp < 15:
        checklist.append("extra sweater")

    # Remove duplicates
    checklist = sorted(set(checklist))

    return message, checklist
