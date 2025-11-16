import streamlit as st
import pandas as pd

from utils.api_handlers import load_market_data

st.set_page_config(
    page_title="Market Price Tracker",
    layout="wide"
)

st.title("📈 Market Price Tracker")

st.markdown("---")

# ----------------------
# 2. MARKET DATA TRACKER
# ----------------------
st.header("📊 Local Market Price Data")

market_df = load_market_data()

if market_df is None or market_df.empty:
    st.warning("Market data could not be loaded.")
else:
    # Fix column names (optional but recommended)
    market_df = market_df.rename(columns={
        'Min_x0020_Price': 'Min_Price',
        'Max_x0020_Price': 'Max_Price',
        'Modal_x0020_Price': 'Modal_Price'
    })

    # Filter by commodity
    available_items = market_df['Commodity'].unique().tolist()
    selected_item = st.selectbox("Select Commodity:", available_items)

    filtered_df = market_df[market_df['Commodity'] == selected_item]

    st.subheader(f"Price Trend for {selected_item}")

    # Ensure charting works only if column is numeric
    try:
        filtered_df['Modal_Price'] = pd.to_numeric(filtered_df['Modal_Price'], errors='coerce')
        st.line_chart(filtered_df[['Arrival_Date', 'Modal_Price']].set_index('Arrival_Date'))
    except Exception as e:
        st.error(f"Error plotting price chart: {e}")

    st.subheader("Raw Data Table")
    st.dataframe(filtered_df)
