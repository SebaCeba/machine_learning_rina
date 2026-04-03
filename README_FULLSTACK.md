# 🏔️ Refuge Occupancy Forecasting

Aplicación completa de pronóstico de ocupación para refugios usando SARIMAX con contexto del calendario chileno.

## 🎯 Características

- **Backend Flask**: API REST con SARIMAX para pronósticos precisos
- **Frontend React**: Interfaz moderna con gráficos interactivos
- **Calendario Chileno**: Integración de feriados y días sándwich
- **Visual**ización Avanzada**: Gráficos con Recharts, tablas interactivas
- **Export de Datos**: Exportación a CSV de resultados

## 📦 Tecnologías

### Backend
- Python 3.x
- Flask 3.1.3
- statsmodels (SARIMAX)
- pandas, numpy
- Flask-CORS

### Frontend
- React 18
- Vite 8
- Recharts (gráficos)
- Lucide React (iconos)

## 🚀 Instalación y Uso

### 1. Backend Flask

```bash
# Instalar dependencias
.\venv\Scripts\pip.exe install -r requirements.txt

# Iniciar servidor Flask (puerto 5000)
.\start.bat
```

El backend estará disponible en: **http://localhost:5000**

### 2. Frontend React

```bash
# Navegar a la carpeta frontend
cd frontend

# Instalar dependencias (solo la primera vez)
npm install

# Iniciar servidor de desarrollo (puerto 5173)
npm run dev
```

El frontend estará disponible en: **http://localhost:5173**

## 📊 Uso de la Aplicación

1. **Abrir el frontend** en http://localhost:5173
2. **Subir archivo CSV** con formato:
   ```csv
   check_in,check_out,noches
   01-01-2024,03-01-2024,2
   15-02-2024,17-02-2024,2
   ```
3. **Ajustar parámetros** (opcional):
   - Días de pronóstico: 30-90 días
4. **Generar pronóstico**: Click en "Subir y Generar Pronóstico"
5. **Visualizar resultados**:
   - KPI Cards con estadísticas
   - Gráfico histórico + pronóstico con bandas de confianza
   - Tabla de datos con filtros y export

## 📁 Estructura del Proyecto

```
machine_learning_rina/
├── app/                          # Backend Flask
│   ├── __init__.py              # Factory y CORS config
│   ├── routes.py                # Rutas HTML (legado)
│   ├── api_routes.py            # API REST endpoints
│   ├── data_loader.py           # Procesamiento CSV
│   └── model.py                 # Modelos SARIMAX
├── frontend/                     # Frontend React
│   ├── src/
│   │   ├── components/          # Componentes UI
│   │   │   ├── Header.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── StatsCards.jsx
│   │   │   ├── ForecastChart.jsx
│   │   │   └── DataTable.jsx
│   │   ├── services/
│   │   │   └── api.js           # Cliente API
│   │   ├── App.jsx              # Componente principal
│   │   └── main.jsx             # Entry point
│   └── package.json
├── data/                         # Datos y outputs
│   ├── processed/               # Datos procesados
│   ├── outputs/                 # Pronósticos generados
│   └── special_days_cl_2022_2040.csv
├── docs/                         # Documentación
├── templates/                    # HTML legado
├── start.bat                     # Script inicio backend
└── requirements.txt
```

## 🔌 API Endpoints

### POST `/api/forecast`
Sube CSV y genera pronóstico.

**Request:**
- `file`: CSV file (multipart/form-data)
- `forecast_horizon`: Días a pronosticar (30-90, default: 60)

**Response:**
```json
{
  "success": true,
  "historical": [...],
  "forecast": [...],
  "stats": {
    "total_days": 1366,
    "occupied_days": 443,
    "occupancy_rate": 32.4,
    "avg_forecast_occupancy": 41.2,
    "forecast_days": 60,
    "holidays_in_forecast": 0,
    "sandwiches_in_forecast": 0,
    "weekends_in_forecast": 18
  }
}
```

### GET `/api/health`
Health check del servidor.

## 🧪 Modelo SARIMAX

- **Orden no estacional**: (1, 0, 1)
- **Orden estacional**: (1, 0, 1, 7) - periodicidad semanal
- **Variables exógenas**:
  - `is_holiday`: Feriados oficiales chilenos
  - `is_sandwich`: Días sándwich
  - `is_weekend`: Fines de semana

## 📝 Notas

- El backend se recarga automáticamente en modo debug
- El frontend tiene HMR (Hot Module Replacement)
- Los pronósticos se guardan en `data/outputs/`
- Logs de procesamiento en consola del backend

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📜 Licencia

Este proyecto es parte de un sistema de gestión de refugios.

---

**Desarrollado con  ❤️  para gestión de refugios chilenos**
