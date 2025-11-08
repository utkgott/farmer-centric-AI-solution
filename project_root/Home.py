

import streamlit as st

# Configure the default settings for the entire application
st.set_page_config(
    page_title="Project AI: Home",
    page_icon="🧠",
    layout="wide"
)

# --- Home Page Content ---

st.title("🧠 Project AI Assistant, Detector, and Tracker")

st.markdown(
    """
    **Welcome!** This application demonstrates the integration of multiple data science and AI 
    capabilities into a single, cohesive interface.

    Use the navigation menu on the left to explore the different sections of the app:
    
    * **1. 🧠 AI Assistant:** A page dedicated to an LLM-powered assistant (via `api_handlers.py`).
    * **2. 🔍 Detector:** The image analysis page that uses your trained PyTorch model (via `model_inference.py`).
    * **3. 📈 Market/Weather:** The data analysis page that displays local data and external API data 
        (via `api_handlers.py`).
        
    """
)

st.markdown("---")

st.subheader("Project Structure Highlights")
st.code(
    """
project_root/
├── .streamlit/
│   └── secrets.toml        # Securely holds API Keys
├── data/
├── models/                 # Contains disease_detector.pth
├── pages/                  # Streamlit automatically turns these into pages
├── utils/                  # Reusable Python functions (logic separation)
└── Home.py                 # This main entry file
    """, 
    language='text'
)

st.info(
    "💡 **To Run:** Make sure you are in the project_root directory and run: `streamlit run Home.py`"
)