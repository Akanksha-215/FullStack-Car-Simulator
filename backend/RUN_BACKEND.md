# How to Run the Backend in Virtual Environment

## Prerequisites
- Python 3.x installed
- Virtual environment already exists in `backend/venv/`

## Steps to Run the Backend

### Method 1: Using PowerShell (Recommended)

1. **Navigate to the backend directory:**
   ```powershell
   cd backend
   ```

2. **Activate the virtual environment:**
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   
   If you get an execution policy error, run this first:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Install dependencies (if not already installed):**
   ```powershell
   pip install -r ..\requirements.txt
   ```

4. **Run the Flask application:**
   ```powershell
   python app.py
   ```

5. **The backend will start at:** `http://localhost:5000`

### Method 2: Using Command Prompt (CMD)

1. **Navigate to the backend directory:**
   ```cmd
   cd backend
   ```

2. **Activate the virtual environment:**
   ```cmd
   venv\Scripts\activate.bat
   ```

3. **Install dependencies (if not already installed):**
   ```cmd
   pip install -r ..\requirements.txt
   ```

4. **Run the Flask application:**
   ```cmd
   python app.py
   ```

### Method 3: Using the Existing Batch File

Simply run from the project root:
```cmd
start_with_venv.bat
```

This will automatically:
- Activate the virtual environment
- Install dependencies
- Start both backend and frontend servers

## Deactivating the Virtual Environment

When you're done, you can deactivate the virtual environment by running:
```powershell
deactivate
```

## Troubleshooting

- **If virtual environment doesn't exist:** Create it with `python -m venv venv`
- **If dependencies are missing:** Run `pip install -r ..\requirements.txt`
- **If port 5000 is already in use:** Change the port in `app.py` (line 205)




