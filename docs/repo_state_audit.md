# Repository State Audit
**Date:** 2026-04-03  
**Repository:** SebaCeba/machine_learning_rina  
**Purpose:** Refuge occupancy forecasting web application

---

## 1. Current File Tree

```
machine_learning_rina/
├── app/
│   ├── __init__.py           # Flask app factory (template path config)
│   ├── routes.py             # HTTP routes (upload, forecast endpoint)
│   ├── model.py              # Holt-Winters forecasting model
│   ├── data_loader.py        # CSV parsing and time series conversion
│   └── __pycache__/          # Python bytecode (ignored by git)
├── data/
│   ├── CONSOLIDADO REFUGIO.csv          # Main booking data (133 rows, semicolon-delimited)
│   ├── holidays_cl_2022_2040.csv        # Chilean holidays dataset
│   └── special_days_cl_2022_2040.csv    # Special days + holidays + sandwich days
├── models/
│   └── .gitkeep              # Placeholder for model artifacts
├── templates/
│   └── index.html            # Single-page web UI with embedded CSS
├── .git/                     # Git repository metadata
├── .gitignore                # Git ignore rules (excludes venv, .pkl, data/*.csv)
├── .venv/                    # Virtual environment (symlink or duplicate, ignored)
├── venv/                     # Virtual environment (ignored by git)
├── __pycache__/              # Python bytecode (ignored by git)
├── main.py                   # Flask app entry point
├── requirements.txt          # Python dependencies (6 packages)
├── start.bat                 # Windows batch script for auto-setup and launch
└── README.md                 # Project documentation
```

**Total tracked files:** 11  
**Total Python code in app/:** ~9KB (4 files)

---

## 2. Main Folders and Their Contents

### `/app` - Application Core
- **Purpose:** Flask application logic
- **Files:** 
  - `__init__.py` - App factory, config (upload/model folders, 16MB limit)
  - `routes.py` - Single route `/` (GET/POST) for CSV upload and forecast display
  - `model.py` - Holt-Winters Exponential Smoothing (statsmodels)
  - `data_loader.py` - CSV parsing (supports `;` and `,` delimiters, DD-MM-YYYY dates)
- **Dependencies:** Flask, pandas, statsmodels

### `/data` - Data Files
- **Purpose:** Input data storage
- **Files:**
  - `CONSOLIDADO REFUGIO.csv` - Historical booking data (2022-2025, 133 records)
  - `holidays_cl_2022_2040.csv` - Chilean public holidays (structured, comma-delimited)
  - `special_days_cl_2022_2040.csv` - Holidays + sandwich days (behavioral events)
- **Note:** `.gitignore` excludes `data/*.csv` except when explicitly forced
- **Status:** Holiday/special days files are **not currently used** by the forecasting model

### `/models` - Model Artifacts
- **Purpose:** Store trained model files (.pkl)
- **Current state:** Empty (only `.gitkeep` present)
- **Expected use:** Save/load trained Holt-Winters models via pickle

### `/templates` - Web UI
- **Purpose:** Flask HTML templates
- **Files:** `index.html` - Single-page app with:
  - CSV upload form
  - Historical data table (last 30 days)
  - Forecast table (30-day predictions with confidence intervals)
  - Embedded CSS (no external stylesheets)
- **Tech:** Plain HTML, no JavaScript frameworks

### `/docs` - Documentation
- **Purpose:** Documentation files
- **Current state:** Created during this audit
- **Files:** `repo_state_audit.md` (this document)

---

## 3. Main Python Files and Their Purpose

| File | Lines (approx) | Purpose |
|------|----------------|---------|
| `main.py` | 6 | Entry point - imports `create_app()`, runs Flask on port 5000 |
| `app/__init__.py` | 20 | Flask factory pattern - configures upload/model folders, registers routes |
| `app/routes.py` | ~80 | Single route handler - processes CSV uploads, calls forecasting pipeline |
| `app/model.py` | ~70 | Holt-Winters training and forecasting (30-day predictions, confidence intervals) |
| `app/data_loader.py` | ~90 | CSV parsing - detects separator, handles multiple date formats, converts to daily time series |

### Key Implementation Details:
- **Forecasting method:** Holt-Winters Exponential Smoothing (weekly seasonality)
- **Input format:** `check_in`, `check_out`, `noches`, `ingresos_total`
- **Cancellation handling:** `noches=0` treated as cancellations (excluded from analysis)
- **Date parsing:** Supports DD-MM-YYYY, YYYY-MM-DD, mixed formats
- **Encoding:** UTF-8-BOM support for Spanish characters
- **Revenue distribution:** Linear allocation across nights

---

## 4. HTML/Templates/Static Files

| File | Purpose | Tech Stack |
|------|---------|------------|
| `templates/index.html` | Single-page UI for upload and forecast display | HTML5, embedded CSS, no JS |

**UI Features:**
- File upload form (CSV only, client-side validation)
- Error/success message display
- Historical data table (last 30 days)
- Forecast table (30 days with lower/upper bounds)
- Responsive styling (max-width: 1200px)
- Color scheme: Green (#4CAF50) primary, red errors, gray backgrounds

**Missing:**
- No JavaScript (no client-side validation beyond `accept=".csv"`)
- No charts/visualizations (tables only)
- No downloadable forecast output
- No static assets folder (CSS embedded in HTML)

---

## 5. Existing Data Files

| File | Format | Rows | Delimiter | Date Range | Usage Status |
|------|--------|------|-----------|------------|--------------|
| `CONSOLIDADO REFUGIO.csv` | CSV | 133 | `;` | 2022-04-15 to 2025-12-29 | **ACTIVE** (main input) |
| `holidays_cl_2022_2040.csv` | CSV | ~340 | `,` | 2022-2040 | **UNUSED** |
| `special_days_cl_2022_2040.csv` | CSV | ~400+ | `,` | 2022-2040 | **UNUSED** |

### Data Quality Notes (CONSOLIDADO REFUGIO):
- **Schema:** `booking_id;fecha_reserva;check_in;check_out;noches;ingresos_total;plataforma;cantidad_personas;uso_tinaja`
- **Used columns:** `check_in`, `check_out`, `noches`, `ingresos_total`
- **Unused columns:** `booking_id`, `fecha_reserva`, `plataforma`, `cantidad_personas`, `uso_tinaja`
- **Cancellations:** 4 records with `noches=0` (excluded from forecast)
- **Revenue range:** ~100K to ~1.7M CLP per booking
- **Platforms:** Airbnb, Booking, WhatsApp, Instagram, Facebook, Interno (internal), Recomendación

### Holiday/Special Days Files:
- **Purpose (apparent):** Exogenous regressors for forecasting
- **Current integration:** **NONE** - not loaded or used by model
- **Fields:** `date`, `name`, `day_type`, `is_public_holiday`, `is_sandwich`, `category`, `rule_code`

---

## 6. Model-Related Files

### Existing:
- `app/model.py` - Holt-Winters implementation
- `models/.gitkeep` - Empty placeholder folder

### Missing:
- No `.pkl` files (models not persisted yet, despite save/load functions existing)
- No training scripts (training happens on-demand via web upload)
- No Jupyter notebooks for EDA or experimentation
- No hyperparameter configuration files
- No model versioning or metadata (MLflow, DVC, etc.)
- No performance metrics logging (MAE, RMSE, etc.)
- No cross-validation or backtesting scripts

### Model Save/Load Functions:
- **Defined in:** `app/model.py`
- **Status:** Implemented but **unclear if used** (no `.pkl` files found in `/models`)
- **Save logic:** Routes file shows `save_model()` is called after training
- **Load logic:** No route for loading pre-trained models

---

## 7. Gaps and Inconsistencies Detected

### Data Organization:
- ❌ No distinction between raw/processed/output data
- ❌ Holiday files present but unused (orphaned)
- ❌ No sample/example CSV in repo despite `.gitignore` exception for `sample_bookings.csv`
- ❌ No data validation schemas or documentation

### Model Pipeline:
- ❌ No model evaluation metrics captured or displayed
- ❌ No model versioning (all models saved as timestamped `.pkl` with no metadata)
- ❌ No forecast accuracy comparison against actuals
- ❌ No confidence interval visualization (only tables)

### Configuration:
- ❌ No config file (hardcoded values in `__init__.py` and `model.py`)
- ❌ No environment variables (`.env` ignored but not used)
- ❌ No logging configuration (print statements in `data_loader.py`)

### Documentation:
- ✅ README.md exists and is up-to-date
- ❌ No API documentation
- ❌ No data dictionary
- ❌ No model card or performance benchmarks
- ❌ No usage examples beyond README

### Testing:
- ❌ No test files (`tests/` folder missing)
- ❌ No unit tests for data processing
- ❌ No integration tests for forecasting pipeline
- ❌ No CI/CD configuration (GitHub Actions, etc.)

### Deployment:
- ✅ `start.bat` for local Windows deployment
- ❌ No Docker configuration
- ❌ No production WSGI server config (using Flask dev server)
- ❌ No deployment documentation

---

## 8. Conclusion: Current State vs. Requirements

### What Exists Today:

✅ **Working web application:**
- Flask-based upload/forecast interface
- CSV parsing with robust date/delimiter handling
- Holt-Winters forecasting (30-day predictions)
- Basic HTML table output

✅ **Real data:**
- 133 historical bookings (2022-2025)
- Chilean holiday calendar (unused)

✅ **Basic project structure:**
- Modular code (`app/` package)
- Requirements specification
- Git repository with proper `.gitignore`

### What is Missing for a Production Forecasting App:

❌ **Data engineering:**
- No ETL pipeline or data validation
- No processed/cleaned data versioning
- Holiday features not integrated
- No data quality monitoring

❌ **Model improvements:**
- No model evaluation or metrics
- No hyperparameter tuning
- No alternative models (ARIMA, Prophet, LightGBM)
- No ensemble methods

❌ **Observability:**
- No logging framework
- No error tracking
- No performance monitoring
- No audit trail for predictions

❌ **Scalability:**
- Single-threaded Flask dev server
- No database (CSV persistence only)
- No caching
- No async processing for long forecasts

❌ **User features:**
- No forecast visualization (charts/graphs)
- No downloadable reports (CSV/PDF)
- No forecast comparison over time
- No what-if scenarios or parameterization

❌ **Developer experience:**
- No automated tests
- No local development guides beyond README
- No contribution guidelines
- No type hints or docstring standards

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Python files** | 5 |
| **Total Python LOC** | ~266 (estimated) |
| **HTML templates** | 1 |
| **Data files** | 3 (1 active, 2 unused) |
| **Model artifacts** | 0 |
| **Config files** | 3 (requirements.txt, .gitignore, start.bat) |
| **Documentation files** | 2 (README.md, this audit) |
| **Test files** | 0 |
| **Notebooks** | 0 |

---

**End of Audit**
