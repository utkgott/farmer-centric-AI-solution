
import torch
import streamlit as st
from PIL import Image
from torchvision import transforms # Assuming a PyTorch model

# IMPORTANT: Define your exact model architecture/class here!
# This function is a placeholder for your model's class definition
class CustomDiseaseDetector(torch.nn.Module):
    # You MUST paste the exact model class definition from your Colab notebook
    def __init__(self, num_classes=3):
        super().__init__()
        # ... your layers (e.g., resnet backbone, final linear layer) ...
        pass
    def forward(self, x):
        # ... your forward pass ...
        return x

# Use st.cache_resource to load the large model file only once
@st.cache_resource
def load_model():
    # Load the model weights and set to evaluation mode
    model_path = 'models/disease_detector.pth'
    
    # 1. Instantiate the model class (MUST match your Colab code)
    model = CustomDiseaseDetector(num_classes=3)
    
    # 2. Load the state dict (weights)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

def predict_image(image_file, model):
    """Preprocesses the image, runs inference, and returns the result."""
    
    # Define the same transformations used during training/testing in Colab
    transform = transforms.Compose([
        transforms.Resize((224, 224)), # Use your model's required size
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Convert uploaded file to PIL Image
    image = Image.open(image_file).convert('RGB')
    tensor = transform(image).unsqueeze(0) # Add batch dimension
    
    # Run prediction
    with torch.no_grad():
        output = model(tensor)
    
    # Post-process: Get class label and confidence
    probabilities = torch.nn.functional.softmax(output, dim=1)
    predicted_class_idx = torch.argmax(probabilities).item()
    confidence = probabilities[0][predicted_class_idx].item()
    
    # Define your class names (MUST match your Colab training labels)
    class_names = ["Healthy", "Early Blight", "Late Blight"]
    
    return class_names[predicted_class_idx], confidence