import os
import cv2
from PIL import Image
import numpy as np

def determine_acne_severity(image_path):
    """
    Determines the severity level of acne based on the image path.
    
    Args:
        image_path (str): Path to the user's image.
        
    Returns:
        str: Severity level ("leve", "moderado", "severo")
    """
    # Check if the image exists
    if not os.path.exists(image_path):
        return "Error: Image not found"
    
    # Load the image
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "Error: Failed to load image"
    except Exception as e:
        return f"Error: {str(e)}"
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to create a binary image
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # Calculate the number of pixels above the threshold
    count = np.sum(thresh > 127)
    
    # Determine severity based on pixel count
    if count < 5000:
        return "leve"
    elif count < 10000:
        return "moderado"
    else:
        return "severo"
