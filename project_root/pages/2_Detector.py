import streamlit as st
from utils.model_inference import load_model, predict_image
from PIL import Image

st.title("🔍 Crop Disease Detector")
st.markdown("Upload a leaf image for instant diagnosis.")
st.markdown("---")

# Load the model when the app runs
model = load_model()

uploaded_file = st.file_uploader(
    "Choose a leaf image (JPG or PNG)", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # 1. Display the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)
    
    # 2. Run prediction on a button click
    if st.button('Diagnose Crop'):
        with st.spinner('Analyzing image for diseases...'):
            # Call the prediction function
            label, confidence = predict_image(uploaded_file, model)
            
            st.markdown("### Diagnosis Result:")
            
            # Use color-coding based on the prediction
            if "healthy" in label.lower():
                st.success(f"**Status: {label}**")
                st.balloons()
            else:
                st.error(f"**Disease Detected: {label}**")
                
            st.info(f"Confidence: **{confidence:.2%}**")
            
            # Provide actionable advice (you can integrate the LLM here!)
            st.markdown("---")
            st.markdown(f"**Recommended Action for {label}:**")
            # This is a placeholder for more detailed advice.
            # In the future, we can use the AI Assistant to generate recommendations.
            st.write("Please consult with a local agricultural expert for specific treatment options.")