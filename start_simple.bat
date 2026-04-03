@echo off
echo ====================================
echo Sales Forecasting Tool - SIMPLE
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Entorno virtual no encontrado
    echo.
    echo Por favor ejecuta primero: install_manual.bat
    echo.
    pause
    exit /b 1
)

REM Check if Flask is installed
venv\Scripts\pip.exe show Flask >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flask no esta instalado
    echo.
    echo Por favor ejecuta primero: install_manual.bat
    echo.
    pause
    exit /b 1
)

echo ====================================
echo Iniciando aplicacion Flask...
echo ====================================
echo.
echo Abre tu navegador en:
echo.
echo   http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ====================================
echo.

venv\Scripts\python.exe main_simple.py

pause
