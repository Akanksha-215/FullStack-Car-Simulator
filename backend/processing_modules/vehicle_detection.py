
#     else:
#         print(f"Error: Could not read the test image at {test_image_path}")



import cv2
import numpy as np
import os

def process_vehicle_detection(image):
    """
    Detects vehicles in an image using a pre-trained Haar Cascade classifier.
    This method is significantly more accurate for vehicle detection than
    general-purpose contour detection.
    """
    # --- Model Loading ---
    # Construct the full path to the model file
    cascade_path = os.path.join(os.path.dirname(__file__), 'haarcascade_car.xml')

    # Check if the model file exists
    if not os.path.exists(cascade_path):
        # In a real application, you might want to raise a more specific error
        # or handle this case by returning the original image with a warning.
        print(f"Error: Model file not found at {cascade_path}")
        # Draw a warning message on the image itself
        cv2.putText(image, "Error: haarcascade_car.xml not found", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return image

    # Load the pre-trained car detector model
    car_cascade = cv2.CascadeClassifier(cascade_path)
    
    # --- Image Processing ---
    # Convert the image to grayscale, which is required for the Haar Cascade
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # --- Vehicle Detection ---
    # Detect cars in the image. The parameters can be tuned for better results:
    # scaleFactor: How much the image size is reduced at each image scale.
    # minNeighbors: How many neighbors each candidate rectangle should have to retain it.
    # minSize: The minimum possible object size. Objects smaller than this are ignored.
    cars = car_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50)
    )
    
    # --- Drawing Detections ---
    # Create a copy of the original image to draw on
    result_image = image.copy()
    
    # Loop over all detected cars
    for (x, y, w, h) in cars:
        # Draw a green bounding box around each detected vehicle
        cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Add the "Vehicle" label at the top-left of the box
        cv2.putText(result_image, "Vehicle", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    
    return result_image

# You can keep this block for local testing if you want
if __name__ == '__main__':
    # Path to a test image
    test_image_path = 'path/to/your/test_image.jpg' # <-- CHANGE THIS
    
    image = cv2.imread(test_image_path)
    
    if image is not None:
        processed_image = process_vehicle_detection(image)
        cv2.imshow('Accurate Vehicle Detection', processed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print(f"Error: Could not read the test image at {test_image_path}")