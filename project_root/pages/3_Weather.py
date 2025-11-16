# pages/Weather_Dashboard.py
import streamlit as st
import pandas as pd
from utils.api_handlers import get_weather, get_weather_icon, detect_severe_alerts, crop_advisory, irrigation_advice

st.set_page_config(page_title="Farmer Weather Dashboard", layout="wide")
st.title("🌾 Farmer Weather Dashboard")
st.markdown("Get 5-day forecast, charts, alerts and crop advisories.")

col_input, col_crop = st.columns([3,1])
with col_input:
    city_input = st.text_input("Enter City Name (or location):", "Delhi", help="City name, e.g. 'Delhi' or 'Ludhiana,IN'")

with col_crop:
    crop_choice = st.selectbox("Crop (for advisory):", ["Wheat","Rice","Maize","Generic"])

if st.button("Get Weather"):
    with st.spinner("Fetching forecast..."):
        result = get_weather(city_input, days=5)

    if 'error' in result:
        st.error(result['error'])
    else:
        city = result.get("city", city_input)
        current = result.get("current", {})
        daily = result.get("daily", [])

        # Top metrics
        st.subheader(f"Current Weather — {city}")
        icon = get_weather_icon(current.get("weatherCode", None) or current.get("weather_code", None) or 1000)
        cols = st.columns(5)
        cols[0].metric("Location", city)
        cols[1].metric("Temperature (°C)", current.get("temperature", "N/A"))
        cols[2].metric("Humidity (%)", current.get("humidity", "N/A"))
        cols[3].metric("Wind (m/s)", current.get("windSpeed", "N/A"))
        cols[4].metric("Rain Prob (%)", current.get("precipitationProbability", "N/A"))

        st.markdown(f"### {icon} Condition (code: {current.get('weatherCode','N/A')})")
        st.markdown("---")

        # Charts - construct dataframe
        df = pd.DataFrame(daily)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            # Plot temps
            temp_df = df[['temp_min','temp_max']].rename(columns={'temp_min':'Min','temp_max':'Max'})
            st.subheader("Temperature (5-day)")
            st.line_chart(temp_df)

            # Rain probability
            st.subheader("Rain Probability (5-day)")
            rain_df = df[['rain_chance']].rename(columns={'rain_chance':'RainChance'})
            st.line_chart(rain_df)

            # Wind
            st.subheader("Wind Speed (5-day)")
            wind_df = df[['wind_avg']].rename(columns={'wind_avg':'Wind'})
            st.line_chart(wind_df)
        else:
            st.info("No daily forecast data available for charts.")

        st.markdown("---")

        # Alerts (rule-based)
        st.subheader("⚠️ Rule-based Alerts")
        alerts = detect_severe_alerts(result)
        if alerts:
            for a in alerts:
                st.error(a)
        else:
            st.success("No severe alerts detected by rule-set.")

        st.markdown("---")

        # Crop Advisory
        st.subheader("🌱 Crop Advisory")
        advice = crop_advisory(result, crop_choice)
        st.info(advice)

        # Irrigation Advice
        st.subheader("💧 Irrigation Guidance")
        irr = irrigation_advice(result)
        st.info(irr)

        st.markdown("---")
        st.subheader("5-Day Forecast (Readable View)")
        if daily:
          for day in daily:
              d_icon = get_weather_icon(day.get("weather_code"))
              date_str = day.get("date", "")[:10]

              temp_min = day.get("temp_min", "N/A")
              temp_max = day.get("temp_max", "N/A")
              humidity = day.get("humidity", "N/A")   # (Note: Tomorrow.io free tier does NOT give daily humidity)
              rain = day.get("rain_chance", "N/A")

              st.markdown(
                  f"**{date_str}** {d_icon}  \n"
                  f"🌡️ **{temp_min}–{temp_max} °C** | "
                  f"🌧 **Rain Chance:** {rain}%"
              )


        else:
            st.info("No forecast data available.")




       
