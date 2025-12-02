from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
import os
import tempfile
from werkzeug.utils import secure_filename
import base64
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# Create directories if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_video(filename):
    video_extensions = {'mp4', 'avi', 'mov', 'mkv'}
    return filename.rsplit('.', 1)[1].lower() in video_extensions

def lane_detection(image):
    """Lane detection using Hough Transform"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    
    # Region of interest
    height, width = edges.shape
    roi_vertices = np.array([[(0, height), (width/2, height/2), (width, height)]], dtype=np.int32)
    mask = np.zeros_like(edges)
    cv2.fillPoly(mask, roi_vertices, 255)
    masked_edges = cv2.bitwise_and(edges, mask)
    
    # Hough lines
    lines = cv2.HoughLinesP(masked_edges, 1, np.pi/180, 50, minLineLength=100, maxLineGap=50)
    
    result = image.copy()
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(result, (x1, y1), (x2, y2), (0, 255, 0), 3)
    
    return result

def vehicle_detection(image):
    """Vehicle detection using Haar Cascade"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Load pre-trained car cascade classifier
    car_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_cars.xml')
    cars = car_cascade.detectMultiScale(gray, 1.1, 3)
    
    result = image.copy()
    for (x, y, w, h) in cars:
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(result, 'Vehicle', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    return result

def pedestrian_detection(image):
    """Pedestrian detection using HOG descriptor"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Load HOG descriptor for pedestrian detection
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    boxes, weights = hog.detectMultiScale(gray, winStride=(8, 8))
    
    result = image.copy()
    for (x, y, w, h) in boxes:
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.putText(result, 'Pedestrian', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    
    return result

def traffic_sign_recognition(image):
    """Basic traffic sign detection using color filtering"""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define color ranges for traffic signs (red and blue)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    
    # Create masks
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    
    mask = mask_red1 + mask_red2 + mask_blue
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    result = image.copy()
    for contour in contours:
        if cv2.contourArea(contour) > 1000:  # Filter small contours
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(result, 'Traffic Sign', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
    
    return result

def object_tracking(image):
    """Basic object tracking using background subtraction"""
    # For static images, we'll use a simple approach
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (21, 21), 0)
    
    # Simple thresholding for demonstration
    _, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    result = image.copy()
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Filter small contours
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result, (x, y), (x+w, y+h), (255, 255, 0), 2)
            cv2.putText(result, 'Object', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
    
    return result

def process_image(image, parameters):
    """Process image with selected parameters"""
    result = image.copy()
    
    for param in parameters:
        if param == 'lane_detection':
            result = lane_detection(result)
        elif param == 'vehicle_detection':
            result = vehicle_detection(result)
        elif param == 'pedestrian_detection':
            result = pedestrian_detection(result)
        elif param == 'traffic_sign_recognition':
            result = traffic_sign_recognition(result)
        elif param == 'object_tracking':
            result = object_tracking(result)
    
    return result

def process_video(video_path, parameters):
    """Process video with selected parameters"""
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create output video writer
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_video.mp4')
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame
        processed_frame = process_image(frame, parameters)
        out.write(processed_frame)
    
    cap.release()
    out.release()
    
    return output_path

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        parameters = request.form.getlist('parameters[]')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        if not parameters:
            return jsonify({'error': 'No parameters selected'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process file
        if is_video(filename):
            # Process video
            output_path = process_video(filepath, parameters)
            
            # Convert to base64 for response
            with open(output_path, 'rb') as video_file:
                video_data = video_file.read()
                video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            return jsonify({
                'success': True,
                'type': 'video',
                'data': video_base64,
                'filename': 'processed_video.mp4'
            })
        else:
            # Process image
            image = cv2.imread(filepath)
            processed_image = process_image(image, parameters)
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', processed_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                'success': True,
                'type': 'image',
                'data': image_base64,
                'filename': 'processed_image.jpg'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/parameters', methods=['GET'])
def get_parameters():
    """Get available processing parameters"""
    parameters = [
        {'id': 'lane_detection', 'name': 'Lane Detection'},
        {'id': 'vehicle_detection', 'name': 'Vehicle Detection'},
        {'id': 'pedestrian_detection', 'name': 'Pedestrian Detection'},
        {'id': 'traffic_sign_recognition', 'name': 'Traffic Sign Recognition'},
        {'id': 'object_tracking', 'name': 'Object Tracking'}
    ]
    return jsonify(parameters)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 