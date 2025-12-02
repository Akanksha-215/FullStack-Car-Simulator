# Computer Vision Project Setup Guide

## Prerequisites

### Required Software
1. **Python 3.8+** - Download from [python.org](https://python.org)
2. **Node.js 16+** - Download from [nodejs.org](https://nodejs.org)
3. **Git** - Download from [git-scm.com](https://git-scm.com)

### System Requirements
- Windows 10/11, macOS, or Linux
- At least 4GB RAM
- 2GB free disk space

## Quick Start (Windows)

1. **Clone or download the project**
2. **Run the startup script:**
   ```cmd
   start.bat
   ```
3. **Wait for both servers to start**
4. **Open your browser and go to:** http://localhost:3000

## Quick Start (Linux/Mac)

1. **Clone or download the project**
2. **Make the script executable:**
   ```bash
   chmod +x start.sh
   ```
3. **Run the startup script:**
   ```bash
   ./start.sh
   ```
4. **Wait for both servers to start**
5. **Open your browser and go to:** http://localhost:3000

## Manual Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Start the Flask server:**
   ```bash
   python app.py
   ```

4. **Backend will be available at:** http://localhost:5000

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

4. **Frontend will be available at:** http://localhost:3000

## Project Structure

```
├── backend/                 # Python Flask API
│   ├── app.py              # Main Flask application
│   └── uploads/            # Uploaded files (auto-created)
├── frontend/               # React application
│   ├── public/             # Static files
│   ├── src/                # React components
│   └── package.json        # Node.js dependencies
├── requirements.txt         # Python dependencies
├── start.bat              # Windows startup script
├── start.sh               # Linux/Mac startup script
└── README.md              # Project documentation
```

## Features

### Computer Vision Algorithms
- **Lane Detection** - Uses Hough Transform for road lane detection
- **Vehicle Detection** - Uses Haar Cascade for car detection
- **Pedestrian Detection** - Uses HOG descriptor for people detection
- **Traffic Sign Recognition** - Uses color filtering for sign detection
- **Object Tracking** - Basic object detection and tracking

### Supported File Formats
- **Images:** JPG, PNG, GIF
- **Videos:** MP4, AVI, MOV, MKV

## Usage

1. **Upload a file** - Drag and drop or click to select an image or video
2. **Select parameters** - Choose which computer vision algorithms to apply
3. **Click Generate** - Process the file with selected algorithms
4. **View results** - See the processed output with detected objects highlighted

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Backend: Change port in `backend/app.py` line 200
   - Frontend: React will automatically suggest an alternative port

2. **Python dependencies not found:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Node.js dependencies not found:**
   ```bash
   cd frontend
   npm install
   ```

4. **OpenCV installation issues:**
   ```bash
   pip install opencv-python-headless
   ```

### Backend Health Check
Visit http://localhost:5000/api/health to verify the backend is running.

### Frontend Health Check
The React app will show an error if it can't connect to the backend.

## Development

### Adding New Algorithms
1. Add the algorithm function in `backend/app.py`
2. Add the parameter to the `/api/parameters` endpoint
3. Update the `process_image` function to handle the new algorithm

### Customizing the UI
1. Modify components in `frontend/src/App.js`
2. Update styles in `frontend/src/index.css`
3. Add new dependencies in `frontend/package.json`

## Team Information

Update the team information in `frontend/src/App.js`:
```javascript
const teamMembers = [
  "Your Name",
  "Team Member 2", 
  "Team Member 3"
];
const guideName = "Your Guide Name";
```

## License

This project is for educational purposes. 