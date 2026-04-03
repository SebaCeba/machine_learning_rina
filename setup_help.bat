@echo off
echo ====================================
echo Sales Forecasting Tool - Quick Setup
echo ====================================
echo.
echo IMPORTANTE: Prophet requiere dependencias especiales en Windows
echo.
echo Por favor sigue estos pasos:
echo.
echo 1. Instala Visual C++ Build Tools desde:
echo    https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo.
echo 2. O usa Anaconda/Miniconda (recomendado):
echo    - Descarga Miniconda: https://docs.conda.io/en/latest/miniconda.html
echo    - Ejecuta: conda create -n forecast python=3.10
echo    - Ejecuta: conda activate forecast
echo    - Ejecuta: conda install -c conda-forge prophet flask pandas
echo.
echo 3. Si tienes problemas, usa la version alternativa:
echo    - Ejecuta: start_alternative.bat
echo.
pause
