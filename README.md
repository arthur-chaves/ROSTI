# ROSTI  
**Recommendations for Outdoor Swims, Transport & Ideas**

ROSTI is your friendly Swiss day trip planner, combining real-time weather, lake water temperatures, transport options, and fun entertainment ideas all in one easy-to-use spot.

Perfect for those sunny summer days when you wonder:

“Which lake is calling me today? Is the water ready for a swim or still too chilly?”

ROSTI helps you make the best choice, so you can enjoy the perfect day outdoors without the guesswork.

---

## Features

- Recommends lakes based on weather, temperature and daylight
- Adjusts daily packing checklist depending on forecast
- Shows public transport options (departure, duration, summary)
- Suggests movies from your personal watchlist
- Built with a real data pipeline using Airflow + PostgreSQL
- Modular and extensible architecture

---

### Tools & Frameworks

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) ![Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?logo=apache-airflow&logoColor=white) ![Spotify](https://img.shields.io/badge/Spotify-1DB954?logo=spotify&logoColor=white)  ![RSS](https://img.shields.io/badge/RSS-F26522?logo=rss&logoColor=white)

---

### Data Sources

- Google Maps API (weather & transit)  
- AlpLakes
- Personal watchlist CSV (Letterboxd export)
- Spotify API
- Wired news (RSS)

---

## Data Pipeline

The `dag_main.py` is an Airflow DAG that runs daily at 8:00 AM to orchestrate the data fetching and processing tasks needed by the ROSTI app.

It performs the following steps:

- Fetches daily weather forecast for the user’s location and saves it as JSON.
- Generates a swim packing checklist based on the weather forecast.
- Retrieves current lake water temperatures for multiple swim spots.
- Gathers public transport information and estimated travel times from the user’s city to all swim spots, including route summaries and Google Maps links.
- Shows the latest episodes from curated podcasts for daily recommendations.

All resulting data files are saved in the `src/data/output/` directory and consumed by the Streamlit app to provide up-to-date, personalized recommendations for outdoor swims, transport, and entertainment.

This DAG ensures that all relevant data is fresh and synchronized every day to deliver an optimal user experience.

---

## 📬 Contact

Connect with me on  [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arthur-chaves-innecco/)

---

ROSTI is best served with sunlight and a towel. Have fun!

Please note that many architectural choices and decisions in this project may not make the most efficient sense, intentionally made for the sake of practicing and learning.
