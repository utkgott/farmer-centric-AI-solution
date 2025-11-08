

import requests
import pandas as pd
import streamlit as st
import os

# --- OpenWeatherMap API Handler ---

@st.cache_data(ttl=3600)  # Cache results for 1 hour (3600 seconds)
def get_weather(city_name):
    """
    Fetches current weather data from OpenWeatherMap using the API key 
    stored securely in Streamlit secrets.toml.
    """
    
    # 1. Retrieve API Key
    try:
        # Securely retrieve the API key from the secrets file
        api_key = st.secrets["OPENWEATHER_API_KEY"]
    except KeyError:
        return {"error": "OpenWeatherMap API Key not found in Streamlit secrets.toml."}

    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"  # Use 'metric' for Celsius, 'imperial' for Fahrenheit
    }
    
    # 2. Make the API Request
    try:
        response = requests.get(BASE_URL, params=params)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status() 
        data = response.json()
        
        # 3. Parse and Return Data
        if data.get("cod") == 200:
            return {
                "city": data.get('name'),
                "temperature": data['main']['temp'],
                "description": data['weather'][0]['description'],
                "humidity": data['main']['humidity'],
                "wind_speed": data['wind']['speed']
            }
        else:
            # Handle API-specific errors (e.g., city not found, usually cod 404)
            return {"error": f"City not found or API error: {data.get('message', 'Unknown error')}"}
            
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors like 404 or 500
        return {"error": f"HTTP Error during API call: Invalid city name or request issue. ({e})"}
    except requests.exceptions.RequestException as e:
        # Handle general network issues (e.g., connection lost)
        return {"error": f"Network error during API call: {e}"}

# --- Market Data Handler ---

@st.cache_data
def load_market_data(file_name="market_prices.csv"):
    """
    Loads a pandas DataFrame from the local CSV file in the 'data' folder.
    The data is cached by Streamlit to load only once.
    """
    
    # Dynamically find the path: Navigate from 'utils' folder up to 'project_root' 
    # then down into 'data'
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', file_name)

    try:
        df = pd.read_csv(file_path)
        
        # Data Cleaning/Preparation: Convert 'Date' to datetime and set as index
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.set_index('Date').sort_index()
            
        return df
        
    except FileNotFoundError:
        st.error(f"Error: The data file '{file_path}' was not found. Check the 'data' folder.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred while reading the CSV: {e}")
        return pd.DataFrame()