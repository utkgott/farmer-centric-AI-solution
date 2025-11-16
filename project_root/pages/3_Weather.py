import streamlit as st
import pandas as pd

# Import handler functions
from utils.api_handlers import get_weather

st.set_page_config(
    page_title="Weather Tracker",
    layout="wide"
)

st.title("Weather Tracker")
st.markdown("---")

# ----------------------
# 1. WEATHER TRACKER
# ----------------------
st.header("🌦️ Current Weather Data")

city_input = st.text_input(
    "Enter City Name:", 
    "Delhi", 
    help="E.g., London, Tokyo, New York"
)

if st.button("Get Weather"):
    with st.spinner(f"Fetching weather for {city_input}..."):
        weather_data = get_weather(city_input)

    if weather_data is None:
        st.error("No response received from weather API.")
    elif 'error' in weather_data:
        st.error(weather_data['error'])
    else:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(label="Location", value=weather_data.get('city', 'N/A'))

        with col2:
            st.metric(label="Temperature", value=f"{weather_data.get('temperature', 'N/A')} °C")

        with col3:
            st.metric(label="Condition", value=weather_data.get('description', 'N/A').title())

        with col4:
            st.metric(label="Humidity", value=f"{weather_data.get('humidity', 'N/A')} %")

