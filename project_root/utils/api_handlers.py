import requests
import streamlit as st
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

# --- Weather API Handler ---

BASE_URL = "https://api.tomorrow.io/v4/timelines"

@st.cache_data(ttl=1800)
def get_weather(city_name: str, days: int = 5) -> Dict[str, Any]:
    """
    Returns:
      {
        "city": city_name,
        "current": {temperature, humidity, windSpeed, precipitationProbability, weatherCode, time},
        "daily": [ {date, temp_min, temp_max, rain_chance, wind_avg, weather_code}, ... up to `days` ]
      }
    """
    try:
        api_key = st.secrets["TOMORROW_API_KEY"]
    except KeyError:
        return {"error": "Tomorrow.io API Key not found in Streamlit secrets.toml."}

    # Request hourly + daily timesteps with fields appropriate for Free tier
    params = {
        "location": city_name,
        "timesteps": "1h,1d",
        "fields": ",".join([
            "temperature", "humidity", "windSpeed", "precipitationProbability",
            "weatherCode", "temperatureMax", "temperatureMin"
        ]),
        "units": "metric",
        "apikey": api_key
    }

    try:
        res = requests.get(BASE_URL, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {e} - {res.text if 'res' in locals() else ''}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}

    # Basic validation
    timelines = data.get("data", {}).get("timelines", [])
    if not timelines:
        return {"error": "No timeline data returned from Tomorrow.io"}

    # Extract hourly timeline (find entry with timestep "1h") and daily ("1d")
    hourly_tl = next((t for t in timelines if t.get("timestep") == "1h"), None)
    daily_tl = next((t for t in timelines if t.get("timestep") == "1d"), None)

    if not hourly_tl or not daily_tl:
        return {"error": "Missing hourly or daily timeline in API response."}

    # Current = first hourly values
    try:
        current_entry = hourly_tl["intervals"][0]
        current_vals = current_entry["values"]
        current = {
            "temperature": current_vals.get("temperature"),
            "humidity": current_vals.get("humidity"),
            "windSpeed": current_vals.get("windSpeed"),
            "precipitationProbability": current_vals.get("precipitationProbability"),
            "weatherCode": current_vals.get("weatherCode"),
            "time": current_entry.get("startTime")  # ISO string
        }
    except Exception:
        current = {}

    # Build daily list
    daily_list: List[Dict[str, Any]] = []
    for d in daily_tl.get("intervals", [])[:days]:
        vals = d.get("values", {})
        daily_list.append({
            "date": d.get("startTime")[:10],
            "temp_max": vals.get("temperatureMax"),
            "temp_min": vals.get("temperatureMin"),
            "rain_chance": vals.get("precipitationProbability"),
            "wind_avg": vals.get("windSpeed"),
            "weather_code": vals.get("weatherCode")
        })

    return {"city": city_name, "current": current, "daily": daily_list}

def get_weather_icon(code: int) -> str:
    icons = {
        1000: "☀️", 1100: "🌤️", 1101: "⛅", 1102: "☁️", 1001: "🌥️",
        4000: "🌧️", 4001: "🌧️", 4200: "🌦️", 4201: "🌧️",
        5000: "❄️", 6000: "🌫️"
    }
    return icons.get(code, "🌡️")

def detect_severe_alerts(weather: Dict[str, Any]) -> list:
    """
    Produces rule-based alerts from forecast (since free tier lacks built-in alerts).
    Rules are conservative and transparent.
    """
    alerts = []
    curr = weather.get("current", {})
    if curr:
        # Heavy rain soon
        p = curr.get("precipitationProbability")
        if p is not None and p >= 70:
            alerts.append("High probability of heavy rain in the next hour (>=70%). Protect harvested crops and check drainage.")

        # Very high temperature
        t = curr.get("temperature")
        if t is not None and t >= 40:
            alerts.append("Very high temperature (>=40°C). Take measures to reduce heat stress on crops and workers.")

        # High wind
        w = curr.get("windSpeed")
        if w is not None and w >= 15:
            alerts.append("High winds forecasted (>=15 m/s). Secure lightweight structures and avoid spraying.")

    # Scan daily forecasts for multi-day alerts
    for day in weather.get("daily", []):
        if (day.get("rain_chance") or 0) >= 80:
            alerts.append(f"Heavy rain likely on {day['date']} (>=80% chance).")
        if (day.get("temp_max") or -999) >= 40:
            alerts.append(f"Extreme heat expected on {day['date']} (max >=40°C).")

    return alerts

def crop_advisory(weather: Dict[str, Any], crop: str = "wheat") -> str:
    """
    Simple rule-based crop advice. Extend rules for more crops.
    """
    # use current & next day
    current = weather.get("current", {})
    daily = weather.get("daily", [])

    temp = current.get("temperature")
    rain = current.get("precipitationProbability")

    crop = crop.lower()
    if crop in ["wheat", "barley"]:
        # Avoid spraying if rain likely soon
        if rain is not None and rain >= 40:
            return "Rain expected soon — postpone pesticide/fertilizer spraying."
        if temp is not None and temp >= 35:
            return "High temperature — irrigate early morning or late evening to reduce stress."
        return "Conditions look normal for field operations. Monitor rain chance before spraying."
    elif crop in ["rice"]:
        # rice needs water: if low rain chance and high temp -> irrigate
        if rain is not None and rain <= 20 and (temp is not None and temp >= 30):
            return "Low rain chance and high temp — consider irrigation to maintain paddy water level."
        return "Monitor standing water and rainfall; schedule irrigation if rain stays low."
    elif crop in ["maize","corn"]:
        if rain is not None and rain >= 50:
            return "High rain chance — ensure field drainage to avoid waterlogging."
        return "Okay for operations; ensure irrigation during dry spells."
    else:
        # generic
        if rain is not None and rain >= 50:
            return "High probability of rain — avoid chemical spraying and protect harvested crops."
        return "No specific advisory. Monitor rainfall and temperature."

def irrigation_advice(weather: Dict[str, Any]) -> str:
    """
    Heuristic irrigation advice when soil moisture/ET not available.
    Simple rule: if rain chance low and daytime temps high => suggest irrigation soon.
    """
    daily = weather.get("daily", [])
    if not daily:
        return "Insufficient forecast data for irrigation advice."

    next_day = daily[0]
    rain = (next_day.get("rain_chance") or 0)
    tmax = next_day.get("temp_max")

    if rain >= 50:
        return "Substantial chance of rain tomorrow — postpone irrigation."
    if tmax is not None and tmax >= 34 and rain <= 20:
        return "High temperatures and low rain chance — consider irrigating tomorrow morning."
    if tmax is not None and tmax < 20 and rain <= 20:
        return "Cool conditions — irrigation may be deferred."
    return "Monitor rainfall and crop growth; use soil checks for final decision."




# --- Market Data Handler ---

@st.cache_data
def load_market_data(file_name="market_prices.csv"):
    """Loads a pandas DataFrame from the local CSV file in the data folder."""

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', file_name)

    try:
        df = pd.read_csv(file_path)

        # Convert date column
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date').sort_index()

        return df

    except FileNotFoundError:
        st.error(f"Error: The data file '{file_path}' was not found.")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"An error occurred while reading the CSV: {e}")
        return pd.DataFrame()
