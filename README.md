<h1 align="center">🏊‍♂️ ROSTI</h1>
<p align="center"><strong>Recommendations for Outdoor Swims, Transport & Ideas</strong></p>



You know those vacation mornings when you wake up and have no idea what to do?
Well, here’s my take as a data engineer :)

ROSTI puts together in a Streamlit app real-time weather, lake water temps, transport info, and some entertainment ideas all in one place to help me decide quickly which lake is calling me today and whether the water is ready for a swim or still too chilly, so I can grab my towel and get going. 

Along the way, it keeps me updated with the latest news and podcasts, and even suggests a movie to watch when the day winds down. No stress, just summer vibes. 😎

---

## Features

- Shows forecasted lake water temperatures for the day
- Adjusts daily packing checklist depending on forecast
- Shows public transport options (departure, duration, summary)
- Suggests movies from my personal watchlist
- Recommends new episodes from my favorite podcasts
- Displays fresh Wired news to read on the way
- Built with a real data pipeline using Airflow + PostgreSQL
- Modular and extensible architecture

---

### Tools & Frameworks

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) ![Airflow](https://img.shields.io/badge/Apache_Airflow-017CEE?logo=apache-airflow&logoColor=white) ![Spotify](https://img.shields.io/badge/Spotify-1DB954?logo=spotify&logoColor=white)  ![RSS](https://img.shields.io/badge/RSS-F26522?logo=rss&logoColor=white)

---

### Data Sources

- Google Maps API (weather & transit)  
- AlpLakes
- Personal watchlist from Letterboxd
- Spotify API
- Wired news (RSS)

## Installation

### Clone the repository

```bash
git clone https://github.com/arthur-chaves/ROSTI.git
cd rosti
```

### Set up environment variables

Create a `.env` file at the root with your credentials, API keys and preferences. All required variables are listed in the `.env.example` file.

---

## Running the Project

Before starting the project, you need to initialize the environment.  
This sets your local user ID for Airflow to avoid permission issues:

```bash
echo -e "AIRFLOW_UID=$(id -u)" > .env
```
The entire infrastructure runs through Docker Compose. To bring up all services, run:

```bash
docker compose up
```

This will start both:

-  the Airflow app at [http://localhost:8080](http://localhost:8080)
-  the Streamlit app at [http://localhost:8501](http://localhost:8501)

## Finalizing Setup

To make full use of the project, you need to manually load some base data into the database:

### 1. Insert your preferred lake swim spots

Either directly in the database, or by editing `db_init.py` with your favorite lakes in Switzerland.

### 2. Add your favorite movies

You can either:

- Import a CSV into the database (e.g., your Letterboxd watchlist), or  
- Manually insert them into the `letterboxd_watchlist` table.

### 3. Initialize the databases

Run the init script from inside any running Airflow container:

```bash
docker exec -it <airflow-container-name> bash
cd dags/src/app/utils
python db_init.py
```
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

## Friendly Reminders

📬 Contact - Connect with me on  [![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/arthur-chaves-innecco/)

ROSTI is best served with sunlight and a towel. Have fun!

Please note that many architectural choices and decisions in this project may not make the most efficient sense, intentionally made for the sake of practicing and learning.

To support the sustainability of third-party and open-source services, please cache API responses whenever possible. This helps avoid unnecessary load and keeps things running smoothly for everyone. :)

## 📄 License

This project is licensed under the [MIT License](LICENSE).
