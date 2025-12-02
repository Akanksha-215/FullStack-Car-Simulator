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

# Import processing modules
from processing_modules.lane_detection import process_lane_detection
from processing_modules.vehicle_detection import process_vehicle_detection
from processing_modules.traffic_sign_recognition import process_traffic_sign_recognition
from processing_modules.object_tracking import process_object_tracking, create_background_subtractor
from processing_modules.distance_estimation import process_distance_estimation

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
# image.png
# Processing functions are now imported from modules

def process_image(image, parameters):
    """Process image with selected parameters using modular functions"""
    result = image.copy()
    
    for param in parameters:
        if param == 'lane_detection':
            result = process_lane_detection(result)
        elif param == 'vehicle_detection':
            result = process_vehicle_detection(result)
        elif param == 'traffic_sign_recognition':
            result = process_traffic_sign_recognition(result)
        elif param == 'object_tracking':
            result = process_object_tracking(result)
        elif param == 'distance_estimation':
            result = process_distance_estimation(result)
    
    return result

def process_image_individual(image, parameters):
    """Process image with individual parameters and return separate results"""
    individual_results = {}
    
    for param in parameters:
        result = image.copy()
        if param == 'lane_detection':
            result = process_lane_detection(result)
        elif param == 'vehicle_detection':
            result = process_vehicle_detection(result)
        elif param == 'traffic_sign_recognition':
            result = process_traffic_sign_recognition(result)
        elif param == 'object_tracking':
            result = process_object_tracking(result)
        elif param == 'distance_estimation':
            result = process_distance_estimation(result)
        
        individual_results[param] = result
    
    return individual_results

def process_video(video_path, parameters, output_path=None):
    """Process video with selected parameters using modular functions"""
    cap = cv2.VideoCapture(video_path)
    
    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create output video writer
    if output_path is None:
        output_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_video.mp4')
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Create background subtractor for object tracking if needed
    background_subtractor = None
    if 'object_tracking' in parameters:
        background_subtractor = create_background_subtractor()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process frame with modular functions
        processed_frame = process_image(frame, parameters)
        
        # Special handling for object tracking in video
        if 'object_tracking' in parameters and background_subtractor is not None:
            processed_frame = process_object_tracking(frame, is_video_frame=True, background_subtractor=background_subtractor)
        
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
            individual_results = process_image_individual(image, parameters)
            
            # Convert combined result to base64
            _, buffer = cv2.imencode('.jpg', processed_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Convert individual results to base64
            individual_base64 = {}
            for param, result_img in individual_results.items():
                _, buffer = cv2.imencode('.jpg', result_img)
                individual_base64[param] = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                'success': True,
                'type': 'image',
                'data': image_base64,
                'individual_results': individual_base64,
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
        {'id': 'traffic_sign_recognition', 'name': 'Traffic Sign Recognition'},
        {'id': 'object_tracking', 'name': 'Object Tracking'},
        {'id': 'distance_estimation', 'name': 'Distance Estimation'}
    ]
    return jsonify(parameters)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Backend is running'})

@app.route('/api/forward_port', methods=['POST'])
def forward_port():
    """Handle media processing (images/videos) from a forwarded port"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        parameters = request.form.getlist('parameters[]')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type, supported: images (png, jpg, jpeg, gif) and videos (mp4, avi, mov, mkv)'}), 400
        
        if not parameters:
            return jsonify({'error': 'No parameters selected'}), 400
        
        if is_video(file.filename):
            # Create a temporary file to store the video
            suffix = os.path.splitext(file.filename)[1] or '.mp4'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_video:
                file.save(temp_video.name)
                video_path = temp_video.name
            
            # Process the video
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_output:
                output_path = temp_output.name

            output_path = process_video(video_path, parameters, output_path)
            
            # Read the processed video and encode it in base64
            with open(output_path, 'rb') as video_file:
                video_data = video_file.read()
                video_base64 = base64.b64encode(video_data).decode('utf-8')
            
            # Clean up temporary files
            os.remove(video_path)
            os.remove(output_path)
            
            return jsonify({
                'success': True,
                'type': 'video',
                'data': video_base64,
                'filename': 'processed_video.mp4'
            })
        else:
            # Process image directly from memory
            file_bytes = file.read()
            np_image = np.frombuffer(file_bytes, np.uint8)
            image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

            if image is None:
                return jsonify({'error': 'Unable to read the image file'}), 400

            processed_image = process_image(image, parameters)
            individual_results = process_image_individual(image, parameters)
            
            # Convert combined result to base64
            _, buffer = cv2.imencode('.jpg', processed_image)
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Convert individual results to base64
            individual_base64 = {}
            for param, result_img in individual_results.items():
                _, buffer = cv2.imencode('.jpg', result_img)
                individual_base64[param] = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                'success': True,
                'type': 'image',
                'data': image_base64,
                'individual_results': individual_base64,
                'filename': 'processed_image.jpg'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
 