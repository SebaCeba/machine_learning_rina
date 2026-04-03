@echo off
echo ====================================
echo Sales Forecasting Tool
echo ====================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        echo Asegurate de tener Python instalado
        pause
        exit /b 1
    )
    echo.
    
    echo Instalando dependencias...
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Fallo la instalacion de dependencias
        pause
        exit /b 1
    )
    echo.
)

REM Check if Flask is installed
venv\Scripts\pip.exe show Flask >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    venv\Scripts\pip.exe install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Fallo la instalacion
        pause
        exit /b 1
    )
    echo.
)

echo ====================================
echo Iniciando aplicacion...
echo ====================================
echo.
echo Abre tu navegador en: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ====================================
echo.

venv\Scripts\python.exe main.py

pause
