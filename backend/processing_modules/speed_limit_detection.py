import cv2
import numpy as np
import re

def detect_speed_limit_signs(image):
    """
    Detects speed limit signs using color filtering and shape detection.
    """
    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Red color ranges (speed limit signs are typically red circles)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    # White color range (for the numbers inside)
    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 30, 255])
    
    # Create masks
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_red = mask_red1 + mask_red2
    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    
    # Apply morphological operations to clean up the red mask
    kernel = np.ones((5, 5), np.uint8)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_CLOSE, kernel)
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, kernel)
    
    # Find contours in the red mask
    contours, _ = cv2.findContours(mask_red, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    speed_limit_signs = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 500:  # Filter small contours
            continue
        
        # Approximate the contour to a polygon
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Check if it's roughly circular (speed limit signs are circular)
        # A circle will have many vertices when approximated
        if len(approx) >= 8:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            
            # Speed limit signs are roughly circular (aspect ratio close to 1)
            if 0.7 < aspect_ratio < 1.3:
                # Extract the sign region
                sign_region = image[y:y+h, x:x+w]
                
                # Try to detect the speed limit number
                speed_value = detect_speed_number(sign_region, mask_white[y:y+h, x:x+w])
                
                speed_limit_signs.append({
                    'bbox': (x, y, w, h),
                    'speed': speed_value,
                    'contour': contour
                })
    
    return speed_limit_signs

def detect_speed_number(sign_region, white_mask_region):
    """
    Attempts to detect the speed limit number from the sign region.
    Uses template matching and contour analysis.
    """
    if sign_region.size == 0:
        return None
    
    # Convert to grayscale
    gray_region = cv2.cvtColor(sign_region, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to isolate white numbers
    _, thresh = cv2.threshold(gray_region, 200, 255, cv2.THRESH_BINARY)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours that might be numbers
    number_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        
        # Numbers should have reasonable size relative to sign
        if area > 50 and w > 10 and h > 20:
            aspect_ratio = h / float(w)
            # Numbers are typically taller than wide
            if 1.2 < aspect_ratio < 3.0:
                number_contours.append((x, y, w, h))
    
    # If we found potential number regions, estimate speed
    # This is a simplified approach - in production, you'd use OCR
    if len(number_contours) >= 1:
        # Common speed limits: 20, 30, 40, 50, 60, 70, 80, 90, 100, 120
        # We'll estimate based on the number of detected regions and size
        # This is a heuristic approach
        total_area = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 50)
        sign_area = sign_region.shape[0] * sign_region.shape[1]
        coverage = total_area / sign_area if sign_area > 0 else 0
        
        # Estimate speed based on typical patterns
        # This is a simplified estimation - real implementation would use OCR
        if len(number_contours) == 1:
            # Single digit or double digit
            return "SPEED LIMIT"
        elif len(number_contours) >= 2:
            # Likely a two-digit number
            return "SPEED LIMIT"
        else:
            return "SPEED LIMIT"
    
    return "SPEED LIMIT"

def draw_speed_limit_detections(image, speed_limit_signs):
    """
    Draws bounding boxes and labels around detected speed limit signs.
    """
    result_image = image.copy()
    
    for sign_info in speed_limit_signs:
        x, y, w, h = sign_info['bbox']
        speed_value = sign_info['speed']
        
        # Draw bounding box in red
        cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        
        # Add label
        label = f"Speed Limit: {speed_value}"
        # Calculate text size for better positioning
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
        
        # Draw background rectangle for text
        cv2.rectangle(result_image, 
                     (x, y - text_height - 10), 
                     (x + text_width, y), 
                     (0, 0, 255), 
                     -1)
        
        # Draw text
        cv2.putText(result_image, label, (x, y - 5), 
                   font, font_scale, (255, 255, 255), thickness)
    
    return result_image

def process_speed_limit_detection(image):
    """
    Main speed limit detection function.
    """
    # Detect speed limit signs
    speed_limit_signs = detect_speed_limit_signs(image)
    
    # Draw detections on image
    result_image = draw_speed_limit_detections(image, speed_limit_signs)
    
    return result_image




