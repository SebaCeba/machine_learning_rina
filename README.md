# Sales Forecasting Tool

Aplicación Flask para forecasting de ventas con machine learning.

## ⚠️ IMPORTANTE - Error de Instalación en Windows

Si ejecutaste `start.bat` y te dio error de compilación, **es normal**.

**SOLUCIÓN RÁPIDA:** Lee [LEEME_PRIMERO.txt](LEEME_PRIMERO.txt) o [SOLUCION_ERROR.md](SOLUCION_ERROR.md)

## 🚀 Inicio Rápido

**Versión Simple (RECOMENDADO) ✅**
```bash
start_simple.bat
```
- Instalación fácil, sin problemas
- Usa algoritmo Holt-Winters
- Precisión similar a Prophet

**Versión Avanzada (Requiere configuración)**
```bash
start.bat
```
- Usa Prophet
- Requiere compilador de C en Windows

---

## Project Structure

```
machine_learning_rina/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── model.py
│   └── data_loader.py
├── templates/
│   └── index.html
├── data/
├── models/
├── main.py
├── requirements.txt
└── .gitignore
```

## Quick Start (Windows)

**Option 1: One-click startup**
```bash
start.bat
```
This will automatically create the virtual environment, install dependencies, and start the server.

**Option 2: Manual installation**
```bash
install.bat
start.bat
```

## Manual Installation

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

The app will be available at: http://localhost:5000

## CSV Format

Your CSV file must include these columns:
- `check_in`: Check-in date (YYYY-MM-DD)
- `check_out`: Check-out date (YYYY-MM-DD)
- `noches`: Number of nights
- `ingresos_total`: Total revenue

Example:
```csv
check_in,check_out,noches,ingresos_total
2024-01-01,2024-01-03,2,250.00
2024-01-05,2024-01-08,3,450.00
```

## Features

- CSV file upload
- Data parsing and validation
- Daily time series conversion
- Prophet-based forecasting
- 30-day forecast generation
- Model persistence (.pkl files)
- Simple HTML interface with tables

## Usage

1. Open http://localhost:5000
2. Upload CSV file with historical bookings
3. View historical data and forecast results
4. Trained models are saved in `models/` folder

## Notes

- Maximum file size: 16MB
- No authentication required
- Models are timestamped and saved automatically
- Revenue is distributed evenly across nights stayed
