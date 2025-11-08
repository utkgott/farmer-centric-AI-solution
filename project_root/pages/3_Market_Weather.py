

import streamlit as st
import pandas as pd
# Import the handler functions from the utils directory
from utils.api_handlers import get_weather, load_market_data

st.set_page_config(
    page_title="Market & Weather Tracker",
    layout="wide"
)

st.title("📈 Market Price and Weather Tracker")
st.markdown("---")

# ----------------------
# 1. WEATHER TRACKER
# ----------------------
st.header("🌦️ Current Weather Data")

city_input = st.text_input("Enter City Name:", "Delhi", help="E.g., London, Tokyo, New York")

if st.button("Get Weather"):
    with st.spinner(f"Fetching weather for {city_input}..."):
        weather_data = get_weather(city_input)
    
    if 'error' in weather_data:
        st.error(weather_data['error'])
    else:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label=f"Location", value=weather_data['city'])

        with col2:
            st.metric(label="Temperature", value=f"{weather_data['temperature']} °C")
            
        with col3:
            st.metric(label="Condition", value=weather_data['description'].title())
            
        with col4:
            st.metric(label="Humidity", value=f"{weather_data['humidity']} %")


st.markdown("---")

# ----------------------
# 2. MARKET DATA TRACKER
# ----------------------
st.header("📊 Local Market Price Data")

# Load data using the function from api_handlers.py
market_df = load_market_data()

if not market_df.empty:
    
    # Filter by item
    available_items = market_df['Item'].unique().tolist()
    selected_item = st.selectbox("Select Market Item:", available_items)
    
    filtered_df = market_df[market_df['Item'] == selected_item]

    # Display the price trend as a line chart
    st.subheader(f"Price Trend for {selected_item}")
    
    # Use st.line_chart on the 'Price' column
    st.line_chart(filtered_df['Price'])

    st.subheader("Raw Data Table")
    st.dataframe(filtered_df)