# Sales Forecasting Tool

Aplicación Flask para forecasting de ventas con machine learning (Holt-Winters).

## 🚀 Inicio Rápido

**Windows:**
```bash
start.bat
```

**Manual:**
```bash
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
python main.py
```

Abre tu navegador en: **http://localhost:5000**

## 📋 Estructura del Proyecto

```
machine_learning_rina/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Upload y forecast endpoints
│   ├── model.py             # Holt-Winters forecasting
│   └── data_loader.py       # CSV parsing y time series
├── templates/
│   └── index.html           # Interfaz web
├── data/
│   └── sample_bookings.csv  # Archivo de ejemplo
├── models/                  # Modelos entrenados (.pkl)
├── main.py                  # Entry point
├── requirements.txt         # Dependencias
├── start.bat                # Inicio automático (Windows)
└── README.md
```

## 📝 Formato CSV

Tu archivo CSV debe incluir estas columnas:
- `check_in`: Fecha check-in (DD-MM-YYYY o YYYY-MM-DD)
- `check_out`: Fecha check-out  
- `noches`: Número de noches (0 = cancelación)
- `ingresos_total`: Ingresos totales

**Separador:** Coma (,) o punto y coma (;)

**Ejemplo:**
```csv
check_in,check_out,noches,ingresos_total
15-04-2022,18-04-2022,4,350000
27-06-2022,01-07-2022,4,578580
```

## ✨ Características

- ✅ Upload de CSV (hasta 16MB)
- ✅ Soporta separadores: `,` y `;`
- ✅ Parseo robusto de fechas
- ✅ Manejo de cancelaciones (noches=0)
- ✅ Forecast de 30 días con Holt-Winters
- ✅ Intervalos de confianza
- ✅ Persistencia de modelos (.pkl)
- ✅ Interfaz web simple

## 🔧 Uso

1. Ejecuta `start.bat` (Windows) o `python main.py`
2. Abre http://localhost:5000
3. Sube tu CSV con datos históricos
4. Visualiza el forecast de 30 días
5. Los modelos se guardan en `models/`

## 📦 Dependencias

- Flask 3.1.3
- pandas 3.0.2
- numpy 2.4.4
- scipy 1.17.1
- statsmodels 0.14.6

## 📄 Notas

- Máximo tamaño de archivo: 16MB
- No requiere autenticación
- Las cancelaciones (noches=0) se excluyen automáticamente
- Los ingresos se distribuyen uniformemente por noche
