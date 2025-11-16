import requests
import streamlit as st
import os
import pandas as pd

# --- Weather API Handler ---

@st.cache_data(ttl=3600)
def get_weather(city_name):

    # 1. Retrieve API Key
    try:
        api_key = st.secrets["OPENWEATHER_API_KEY"]
    except KeyError:
        return {"error": "OpenWeatherMap API Key not found in Streamlit secrets.toml."}

    BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "list" not in data:
            return {"error": "Invalid API response. 'list' not found."}

        first_entry = data["list"][0]  # First hour forecast
        city_info = data.get("city", {})

        return {
            "city": city_info.get("name", city_name),
            "temperature": first_entry["main"]["temp"],
            "description": first_entry["weather"][0]["description"],
            "humidity": first_entry["main"]["humidity"],
            "wind_speed": first_entry["wind"]["speed"],
            "time": first_entry["dt"]
        }

    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP Error: {e}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {e}"}


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
