#!/bin/bash

echo "Starting Computer Vision Project..."
echo

echo "Installing Python dependencies..."
cd backend
pip install -r ../requirements.txt
echo

echo "Installing Node.js dependencies..."
cd ../frontend
npm install
echo

echo "Starting backend server..."
cd ../backend
python app.py &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 3

echo "Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo
echo "Both servers are starting..."
echo "Backend will be available at: http://localhost:5000"
echo "Frontend will be available at: http://localhost:3000"
echo
echo "Press Ctrl+C to stop both servers..."

# Wait for user to stop
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait 