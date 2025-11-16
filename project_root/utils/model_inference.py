import torch
import timm
import streamlit as st
from PIL import Image
from torchvision import transforms

# --- Model Loading ---

@st.cache_resource
def load_model():
    """
    Loads the pre-trained EfficientNetV2-Small model and 
    the fine-tuned weights.
    """
    # 1. Define the number of classes your model was trained on
    num_classes = 17  # CORRECTED: Was 38, should be 17

    # 2. Create the model architecture using timm
    model = timm.create_model(
        'tf_efficientnetv2_s',
        pretrained=False,  # We are loading our own weights, so no need to download
        num_classes=num_classes
    )
    
    # 3. Load your fine-tuned weights
    model_path = 'models/EfficientNetV2-Small_best_model.pth'
    try:
        # Load the state dict
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    except FileNotFoundError:
        st.error(f"Model file not found at {model_path}. Please make sure it's in the 'models' directory.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        st.stop()

    # 4. Set the model to evaluation mode
    model.eval()
    return model

# --- Image Prediction ---

def predict_image(image_file, model):
    """
    Preprocesses the uploaded image, runs inference, and returns the 
    predicted class and confidence score.
    """
    
    # 1. Define the same transformations used during training
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # 2. Preprocess the image
    image = Image.open(image_file).convert('RGB')
    tensor = transform(image).unsqueeze(0)  # Add batch dimension
    
    # 3. Run prediction
    with torch.no_grad():
        output = model(tensor)
    
    # 4. Post-process the output
    probabilities = torch.nn.functional.softmax(output, dim=1)
    confidence, predicted_class_idx = torch.max(probabilities, 1)
    
    # 5. Define your class names (MUST match your training labels)
    #    These are the 17 classes from your training script
    class_names = [
        'Corn___Common_Rust', 
        'Corn___Gray_Leaf_Spot', 
        'Corn___Healthy', 
        'Corn___Northern_Leaf_Blight',
        'Potato___Early_Blight', 
        'Potato___Healthy', 
        'Potato___Late_Blight',
        'Rice___Brown_Spot', 
        'Rice___Healthy', 
        'Rice___Leaf_Blast', 
        'Rice___Neck_Blast',
        'Sugarcane__Bacterial_Blight', 
        'Sugarcane__Healthy', 
        'Sugarcane__Red_Rot',
        'Wheat___Brown_Rust', 
        'Wheat___Healthy', 
        'Wheat___Yellow_Rust'
    ]
    
    return class_names[predicted_class_idx.item()], confidence.item()