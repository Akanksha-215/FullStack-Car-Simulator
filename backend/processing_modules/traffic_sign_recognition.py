import cv2
import numpy as np

def detect_traffic_sign_colors(image):
    """
    Detects traffic signs using color filtering for red, blue, and yellow signs.
    """
    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Red color ranges (red wraps around in HSV)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    # Blue color range
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    
    # Yellow color range
    lower_yellow = np.array([15, 80, 120])
    upper_yellow = np.array([35, 255, 255])
    
    # Create masks
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Combine all masks
    combined_mask = mask_red1 + mask_red2 + mask_blue + mask_yellow
    
    return combined_mask

def detect_sign_shapes(contours):
    """
    Detects traffic sign shapes (triangular, circular, rectangular).
    """
    sign_contours = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 1000:  # Filter small contours
            continue
            
        # Approximate the contour to a polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Get the number of vertices
        vertices = len(approx)
        
        # Classify based on shape
        if vertices == 3:  # Triangle (warning signs)
            sign_type = "Warning"
        elif vertices == 4:  # Rectangle (regulatory signs)
            sign_type = "Regulatory"
        elif vertices >= 8:  # Circle (prohibition signs)
            sign_type = "Prohibition"
        else:
            sign_type = "Unknown"
            
        sign_contours.append((contour, sign_type))
    
    return sign_contours

def classify_traffic_sign(contour, image):
    """
    Attempts to classify the specific type of traffic sign.
    """
    # Get bounding rectangle
    x, y, w, h = cv2.boundingRect(contour)
    
    # Extract the sign region
    sign_region = image[y:y+h, x:x+w]
    
    # Simple classification based on color and shape
    # This is a basic implementation - in a real system, you'd use a trained classifier
    
    # Convert to HSV for color analysis
    hsv_region = cv2.cvtColor(sign_region, cv2.COLOR_BGR2HSV)
    
    # Check for red color (stop signs, yield signs)
    red_mask = cv2.inRange(hsv_region, np.array([0, 50, 50]), np.array([10, 255, 255]))
    red_pixels = cv2.countNonZero(red_mask)
    
    # Check for blue color (information signs)
    blue_mask = cv2.inRange(hsv_region, np.array([100, 50, 50]), np.array([130, 255, 255]))
    blue_pixels = cv2.countNonZero(blue_mask)
    
    # Simple classification
    total_pixels = w * h
    red_ratio = red_pixels / total_pixels
    blue_ratio = blue_pixels / total_pixels
    
    if red_ratio > 0.3:
        return "Stop/Yield Sign"
    elif blue_ratio > 0.3:
        return "Information Sign"
    else:
        return "Traffic Sign"

def draw_traffic_sign_detections(image, sign_contours):
    """
    Draws bounding boxes and labels around detected traffic signs.
    """
    result_image = image.copy()
    
    for contour, sign_type in sign_contours:
        x, y, w, h = cv2.boundingRect(contour)
        
        # Determine color based on sign type
        if sign_type == "Warning":
            color = (0, 255, 255)  # Yellow
        elif sign_type == "Regulatory":
            color = (255, 0, 0)    # Blue
        elif sign_type == "Prohibition":
            color = (0, 0, 255)    # Red
        else:
            color = (255, 255, 0)  # Cyan
        
        # Draw bounding box
        cv2.rectangle(result_image, (x, y), (x + w, y + h), color, 2)
        
        # Classify specific sign type
        specific_type = classify_traffic_sign(contour, image)
        
        # Add label
        label = f"{specific_type}"
        cv2.putText(result_image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    return result_image

def process_traffic_sign_recognition(image):
    """
    Main traffic sign recognition function.
    """
    # 1. Detect traffic sign colors
    color_mask = detect_traffic_sign_colors(image)
    
    # 2. Apply morphological operations to clean up the mask
    kernel = np.ones((5, 5), np.uint8)
    cleaned_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)
    cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_OPEN, kernel)
    
    # 3. Find contours
    contours, _ = cv2.findContours(cleaned_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 4. Detect sign shapes
    sign_contours = detect_sign_shapes(contours)
    
    # 5. Draw detections on image
    result_image = draw_traffic_sign_detections(image, sign_contours)
    
    return result_image 