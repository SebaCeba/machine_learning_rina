@echo off
echo ====================================
echo Sales Forecasting Tool - Startup
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [1/3] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Activate virtual environment
echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import flask" 2>nul
if errorlevel 1 (
    echo.
    echo [3/3] Installing dependencies...
    echo This may take a few minutes...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
    echo.
) else (
    echo [3/3] Dependencies already installed.
    echo.
)

REM Start the application
echo ====================================
echo Starting Flask application...
echo Open your browser at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo ====================================
echo.

python main.py

pause
