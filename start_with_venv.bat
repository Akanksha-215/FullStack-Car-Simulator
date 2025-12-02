@echo off
echo Starting Computer Vision Project with Virtual Environment...
echo.

echo Setting up Python virtual environment...
cd backend
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -r ..\requirements.txt
echo.

echo Installing Node.js dependencies...
cd ..\frontend
npm install
echo.

echo Starting backend server...
start "Backend Server" cmd /k "cd ..\backend && call venv\Scripts\activate.bat && python app.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak > nul

echo Starting frontend server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo Backend will be available at: http://localhost:5000
echo Frontend will be available at: http://localhost:3000
echo.
echo Press any key to exit this window...
pause > nul 