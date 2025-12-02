import cv2
import numpy as np

def detect_moving_objects(image, background_subtractor):
    """
    Detects moving objects using background subtraction.
    """
    fg_mask = background_subtractor.apply(image)
    kernel = np.ones((5, 5), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    return fg_mask

def detect_static_objects(image):
    """
    Detects objects in static images with improved noise reduction.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    
    # NEW: Add morphological operations to remove noise and close gaps
    kernel = np.ones((3, 3), np.uint8)
    # Remove small noise specks
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    # Close gaps in potential objects
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def filter_object_contours(contours, min_area=1000, max_area=100000):
    """
    Filters contours with stricter criteria based on shape and solidity.
    """
    filtered_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by area first
        if min_area < area < max_area:
            x, y, w, h = cv2.boundingRect(contour)
            
            # NEW: Filter by Aspect Ratio (width vs. height)
            # This helps to filter out things that are too tall or too wide to be vehicles.
            aspect_ratio = w / float(h)
            if 0.8 < aspect_ratio < 4.0:
                
                # NEW: Filter by Solidity (how "solid" the shape is)
                # This is excellent for removing irregular shapes like foliage.
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                if solidity > 0.5:
                    filtered_contours.append(contour)
                    
    return filtered_contours

def classify_object(contour):
    """
    Classifies the object based on its properties.
    """
    _, _, w, h = cv2.boundingRect(contour)
    area = cv2.contourArea(contour)
    aspect_ratio = w / float(h)
    
    # More specific classification
    if (aspect_ratio > 1.2 and area > 2000):
        return "Vehicle"
    else:
        return "Object"

def draw_object_detections(image, contours):
    """
    Draws green bounding boxes and labels on detected objects.
    """
    result_image = image.copy()
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        object_type = classify_object(contour)
        color = (0, 255, 0) # Green
        cv2.rectangle(result_image, (x, y), (x + w, y + h), color, 2)
        cv2.putText(result_image, object_type, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    return result_image

def process_object_tracking(image, is_video_frame=False, background_subtractor=None):
    """
    Main object tracking function.
    """
    if is_video_frame and background_subtractor:
        fg_mask = detect_moving_objects(image, background_subtractor)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    else:
        contours = detect_static_objects(image)
        
    filtered_contours = filter_object_contours(contours)
    result_image = draw_object_detections(image, filtered_contours)
    return result_image

def create_background_subtractor():
    """
    Creates a background subtractor for video processing.
    """
    return cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=True)