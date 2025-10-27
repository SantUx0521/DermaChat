import os
import cv2
from PIL import Image
import numpy as np

def determine_acne_severity(image_path):
    if not os.path.exists(image_path):
        return "Error: Image not found"
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            return "Error: Failed to load image"
    except Exception as e:
        return f"Error: {str(e)}"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    count = np.sum(thresh > 127)

    if count < 5000:
        return "leve"
    elif count < 10000:
        return "moderado"
    else:
        return "severo"
