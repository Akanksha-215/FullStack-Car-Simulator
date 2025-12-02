import cv2
import numpy as np

def load_hog_detector():
    """
    Loads the HOG descriptor for pedestrian detection.
    """
    try:
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        return hog
    except:
        return None

def detect_pedestrians_hog(image, hog):
    """
    Detects pedestrians using HOG descriptor.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect pedestrians with optimized parameters
    boxes, weights = hog.detectMultiScale(
        gray,
        winStride=(8, 8),
        padding=(4, 4),
        scale=1.05,
        hitThreshold=0,
        finalThreshold=1.3
    )
    
    return boxes, weights

def detect_pedestrians_contour(image):
    """
    Detects pedestrians using contour detection as a fallback method.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply morphological operations to enhance pedestrian shapes
    kernel = np.ones((3, 3), np.uint8)
    morphed = cv2.morphologyEx(blurred, cv2.MORPH_CLOSE, kernel)
    
    # Apply adaptive threshold
    thresh = cv2.adaptiveThreshold(morphed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours based on area and aspect ratio for pedestrian-like shapes
    pedestrian_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500 and area < 20000:  # Filter by area
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = h / float(w)
            if 1.5 < aspect_ratio < 4.0:  # Pedestrians are typically tall and thin
                pedestrian_contours.append((x, y, w, h))
    
    return pedestrian_contours

def draw_pedestrian_detections(image, detections, method="HOG"):
    """
    Draws bounding boxes around detected pedestrians.
    """
    result_image = image.copy()
    
    for (x, y, w, h) in detections:
        # Draw bounding box
        cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # Add label
        label = f"Pedestrian ({method})"
        cv2.putText(result_image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    return result_image

def process_pedestrian_detection(image):
    """
    Main pedestrian detection function with multiple detection methods.
    """
    # Try HOG detector first
    hog = load_hog_detector()
    detections = []
    
    if hog is not None:
        boxes, weights = detect_pedestrians_hog(image, hog)
        detections.extend(boxes)
    
    # If no detections or HOG failed, try contour method
    if len(detections) == 0:
        contour_detections = detect_pedestrians_contour(image)
        detections.extend(contour_detections)
    
    # Draw detections on image
    result_image = draw_pedestrian_detections(image, detections)
    
    return result_image 