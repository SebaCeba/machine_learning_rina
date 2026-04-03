@echo off
echo ====================================
echo Instalacion Sales Forecasting Tool
echo ====================================
echo.

REM Check Python version
python --version
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    pause
    exit /b 1
)

echo.
echo Paso 1: Creando entorno virtual...
if exist venv (
    echo Eliminando entorno virtual anterior...
    rmdir /s /q venv
)
python -m venv venv
echo.

echo Paso 2: Actualizando pip, setuptools y wheel...
venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
echo.

echo Paso 3: Instalando paquetes (esto puede tardar 3-5 minutos)...
echo.
venv\Scripts\pip.exe install Flask Werkzeug numpy pandas scipy statsmodels
if errorlevel 1 (
    echo.
    echo ERROR: Fallo la instalacion
    echo Verifica tu conexion a internet e intenta de nuevo
    pause
    exit /b 1
)
echo.

echo ====================================
echo INSTALACION COMPLETADA CON EXITO!
echo ====================================
echo.
echo Ahora ejecuta: start_simple.bat
echo.
echo O manualmente:
echo   venv\Scripts\python.exe main_simple.py
echo.
echo Luego abre: http://localhost:5000
echo.

pause
