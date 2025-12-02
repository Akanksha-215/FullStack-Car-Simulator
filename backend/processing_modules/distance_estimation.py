import cv2
import numpy as np

# Camera calibration constants (these would ideally come from camera calibration)
# These are approximate values - in production, you'd calibrate your specific camera
FOCAL_LENGTH = 700  # Focal length in pixels (approximate for typical cameras)
KNOWN_WIDTH = 1.8  # Average car width in meters
KNOWN_HEIGHT = 1.5  # Average car height in meters
KNOWN_PERSON_HEIGHT = 1.7  # Average person height in meters

def calculate_distance_by_width(bbox_width, known_width=KNOWN_WIDTH, focal_length=FOCAL_LENGTH):
    """
    Calculates distance to an object using its width in the image.
    Formula: distance = (known_width * focal_length) / pixel_width
    """
    if bbox_width == 0:
        return None
    distance = (known_width * focal_length) / bbox_width
    return distance

def calculate_distance_by_height(bbox_height, known_height=KNOWN_HEIGHT, focal_length=FOCAL_LENGTH):
    """
    Calculates distance to an object using its height in the image.
    Formula: distance = (known_height * focal_length) / pixel_height
    """
    if bbox_height == 0:
        return None
    distance = (known_height * focal_length) / bbox_height
    return distance

def estimate_object_distance(image, bbox, object_type="vehicle"):
    """
    Estimates the distance to a detected object based on its bounding box.
    
    Args:
        image: Input image
        bbox: Bounding box (x, y, w, h)
        object_type: Type of object ('vehicle', 'pedestrian', 'object')
    
    Returns:
        Estimated distance in meters
    """
    x, y, w, h = bbox
    
    # Use appropriate known dimensions based on object type
    if object_type.lower() == "pedestrian" or object_type.lower() == "person":
        # Use height for pedestrians (more reliable)
        distance = calculate_distance_by_height(h, KNOWN_PERSON_HEIGHT, FOCAL_LENGTH)
    elif object_type.lower() == "vehicle" or object_type.lower() == "car":
        # Use width for vehicles (more reliable)
        distance = calculate_distance_by_width(w, KNOWN_WIDTH, FOCAL_LENGTH)
    else:
        # For generic objects, use average of width and height
        distance_w = calculate_distance_by_width(w, KNOWN_WIDTH, FOCAL_LENGTH)
        distance_h = calculate_distance_by_height(h, KNOWN_HEIGHT, FOCAL_LENGTH)
        if distance_w and distance_h:
            distance = (distance_w + distance_h) / 2
        else:
            distance = distance_w or distance_h
    
    return distance

def detect_objects_for_distance(image):
    """
    Detects objects in the image that we can estimate distance for.
    Uses simple contour detection to find potential objects.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive threshold
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 2)
    
    # Morphological operations to clean up
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(closing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours
    objects = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if 1000 < area < 50000:  # Filter by area
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / float(h)
            
            # Classify object type based on aspect ratio
            if 0.8 < aspect_ratio < 2.5:
                # Likely a vehicle (wider than tall)
                objects.append({
                    'bbox': (x, y, w, h),
                    'type': 'vehicle',
                    'contour': contour
                })
            elif 0.3 < aspect_ratio < 0.8:
                # Likely a pedestrian (taller than wide)
                objects.append({
                    'bbox': (x, y, w, h),
                    'type': 'pedestrian',
                    'contour': contour
                })
            else:
                objects.append({
                    'bbox': (x, y, w, h),
                    'type': 'object',
                    'contour': contour
                })
    
    return objects

def draw_distance_estimations(image, objects_with_distances):
    """
    Draws bounding boxes with distance labels on the image.
    """
    result_image = image.copy()
    
    for obj_info in objects_with_distances:
        x, y, w, h = obj_info['bbox']
        distance = obj_info['distance']
        obj_type = obj_info['type']
        
        # Determine color based on distance (closer = red, farther = green)
        if distance < 10:
            color = (0, 0, 255)  # Red - very close
        elif distance < 30:
            color = (0, 165, 255)  # Orange - close
        elif distance < 50:
            color = (0, 255, 255)  # Yellow - medium
        else:
            color = (0, 255, 0)  # Green - far
        
        # Draw bounding box
        cv2.rectangle(result_image, (x, y), (x + w, y + h), color, 2)
        
        # Prepare distance label
        if distance:
            distance_text = f"{obj_type.capitalize()}: {distance:.1f}m"
        else:
            distance_text = f"{obj_type.capitalize()}: N/A"
        
        # Calculate text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (text_width, text_height), baseline = cv2.getTextSize(distance_text, font, font_scale, thickness)
        
        # Draw background rectangle for text
        cv2.rectangle(result_image, 
                     (x, y - text_height - 10), 
                     (x + text_width, y), 
                     color, 
                     -1)
        
        # Draw text
        cv2.putText(result_image, distance_text, (x, y - 5), 
                   font, font_scale, (255, 255, 255), thickness)
        
        # Add warning if too close
        if distance and distance < 15:
            warning_text = "WARNING: TOO CLOSE!"
            (warn_width, warn_height), _ = cv2.getTextSize(warning_text, font, 0.5, 2)
            cv2.rectangle(result_image,
                         (x, y + h),
                         (x + warn_width, y + h + warn_height + 5),
                         (0, 0, 255),
                         -1)
            cv2.putText(result_image, warning_text, (x, y + h + warn_height),
                       font, 0.5, (255, 255, 255), 2)
    
    return result_image

def process_distance_estimation(image):
    """
    Main distance estimation function.
    Detects objects and estimates their distance from the camera.
    """
    # Detect objects in the image
    objects = detect_objects_for_distance(image)
    
    # Estimate distance for each object
    objects_with_distances = []
    for obj in objects:
        distance = estimate_object_distance(image, obj['bbox'], obj['type'])
        objects_with_distances.append({
            'bbox': obj['bbox'],
            'type': obj['type'],
            'distance': distance
        })
    
    # Draw distance estimations on image
    result_image = draw_distance_estimations(image, objects_with_distances)
    
    return result_image




