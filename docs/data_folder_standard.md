# Data Folder Standard
**Repository:** machine_learning_rina  
**Date:** 2026-04-03  
**Based on:** docs/repo_state_audit.md

---

## 1. Current State Summary

### How `data/` is Currently Used:
- **All data types mixed in single folder** - no separation between raw inputs, calendar data, or outputs
- **Three CSV files present:**
  - `CONSOLIDADO REFUGIO.csv` - Historical booking data (133 records, 2022-2025) - **ACTIVE**
  - `holidays_cl_2022_2040.csv` - Chilean public holidays - **UNUSED**
  - `special_days_cl_2022_2040.csv` - Holidays + sandwich days - **UNUSED**

### Main Problems:
❌ **No data type separation** - raw, processed, and calendar data all in root `data/`  
❌ **Orphaned files** - Holiday/special days files exist but never loaded by model  
❌ **No naming standard** - Files use inconsistent formats (spaces, uppercase, underscores)  
❌ **No versioning** - Historical data has no timestamp or version identifier  
❌ **No documentation** - No data dictionary or schema description  
❌ **No processed layer** - Daily aggregations computed on-the-fly, never persisted  
❌ **No output storage** - Forecasts displayed in browser but never saved  

---

## 2. Target Data Folder Structure

```
data/
├── historical/              # Raw booking data (immutable)
│   └── bookings_raw_20220415_20251229.csv
│
├── calendar/                # External calendar inputs (holidays, special days)
│   ├── holidays_cl_2022_2040.csv
│   └── special_days_cl_2022_2040.csv
│
├── parameters/              # Model configuration inputs (future use)
│   └── (empty initially)
│
├── processed/               # Derived datasets (reproducible from raw + code)
│   └── (empty initially)
│
└── outputs/                 # Final forecasts and results
    └── (empty initially)
```

**Rationale:**
- **Minimal change** - Reuses existing `data/` folder
- **Clear separation** - Each subfolder has single, well-defined purpose
- **Backward compatible** - Existing code paths can be updated incrementally
- **Scalable** - Structure supports future features (parameters, feature engineering)

---

## 3. Migration Plan

### File Movements:

| Current Path | Target Path | Action | Reason |
|-------------|-------------|--------|--------|
| `data/CONSOLIDADO REFUGIO.csv` | `data/historical/bookings_raw_20220415_20251229.csv` | **Move + Rename** | Add date range to filename, remove spaces |
| `data/holidays_cl_2022_2040.csv` | `data/calendar/holidays_cl_2022_2040.csv` | **Move** | Separate calendar data from historical |
| `data/special_days_cl_2022_2040.csv` | `data/calendar/special_days_cl_2022_2040.csv` | **Move** | Separate calendar data from historical |

### Code Updates Required:

**Before migration:**
```python
filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
# Saves to: data/bookings_20260403_143022.csv
```

**After migration:**
```python
filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'historical', filename)
# Saves to: data/historical/bookings_20260403_143022.csv
```

**Files to update:**
- `app/__init__.py` - Ensure subfolders are created in `create_app()`
- `app/routes.py` - Update upload path to `historical/`

### `.gitignore` Updates:

**Add:**
```
data/historical/*.csv
data/processed/*.csv
data/outputs/*.csv
!data/historical/bookings_raw_20220415_20251229.csv
```

**Remove:**
```
data/*.csv
!data/sample_bookings.csv
```

---

## 4. Standard File Naming Conventions

### `historical/` - Raw booking data
**Format:** `bookings_raw_YYYYMMDD(_YYYYMMDD).csv`  
**Examples:**
- `bookings_raw_20220415_20251229.csv` - Full historical dataset (date range in name)
- `bookings_raw_20260403.csv` - New upload dated by creation

**Rules:**
- Use `_raw_` to indicate unprocessed data
- Use date range for cumulative datasets
- Use single date for point-in-time uploads
- Always lowercase, underscores only

### `calendar/` - Calendar inputs
**Format:** `{type}_cl_YYYY_YYYY.csv`  
**Examples:**
- `holidays_cl_2022_2040.csv` ✅ (current name is correct)
- `special_days_cl_2022_2040.csv` ✅ (current name is correct)

**Rules:**
- Prefix with data type (`holidays`, `special_days`)
- Include country code (`cl` for Chile)
- Include year range covered
- These are **reference data** - infrequently updated

### `parameters/` - Model configuration
**Format:** `{type}_parameters_{variant}(_YYYYMMDD).csv`  
**Examples:**
- `model_parameters_default.csv` - Default configuration
- `model_parameters_high_season_20260101.csv` - Custom seasonal config
- `pricing_assumptions_20260403.csv` - External pricing inputs

**Rules:**
- Clearly indicate parameter type
- Use `default` for base configuration
- Add timestamp for custom/experimental variants
- Must be CSV for transparency (avoid binary configs)

### `processed/` - Derived datasets
**Format:** `{content}_{granularity}_YYYYMMDD.csv`  
**Examples:**
- `bookings_daily_20260403.csv` - Daily aggregated bookings
- `features_daily_20260403.csv` - Feature matrix for modeling
- `occupancy_weekly_20260403.csv` - Weekly occupancy rates

**Rules:**
- Prefix describes content (`bookings`, `features`, `occupancy`)
- Include aggregation level (`daily`, `weekly`, `monthly`)
- **Must include processing date** (when file was created)
- Must be reproducible from raw data + code version

### `outputs/` - Forecasts and results
**Format:** `forecast_{metric}_YYYYMMDD_HHMMSS.csv`  
**Examples:**
- `forecast_occupancy_20260403_143022.csv` - Occupancy predictions
- `forecast_revenue_20260403_143022.csv` - Revenue predictions
- `model_metrics_20260403_143022.json` - Model performance stats

**Rules:**
- Prefix with `forecast_` or `model_`
- Include metric/output type
- **Always timestamped** (date + time for uniqueness)
- JSON allowed for metadata/metrics

---

## 5. Folder Purposes

### `historical/` - Raw Booking Data
**Purpose:** Store immutable historical booking records  
**Characteristics:**
- **Immutable** - Files are never modified after upload
- **Source of truth** - All analysis starts here
- **Versioned by filename** - Date ranges or upload timestamps
- **Backed up** - Critical business data (though `.gitignore`d)

**Current state:** Will contain 1 file after migration

---

### `calendar/` - External Calendar Inputs
**Purpose:** Store official and behavioral calendar data (holidays, sandwich days, events)  
**Characteristics:**
- **Shared reference data** - Used across all models/forecasts
- **Infrequently updated** - Only when official calendar changes
- **Versioned by year range** - Covers multi-year periods
- **Tracked in git** - Small, stable files safe to version

**Current state:** Will contain 2 files after migration (currently unused by model)

---

### `parameters/` - Model Configuration Inputs
**Purpose:** Store user-configurable assumptions and model parameters  
**Characteristics:**
- **Future feature** - Not yet implemented
- **Transparent configs** - CSV for auditability (not YAML/JSON)
- **Versioned by use case** - Different configs for different scenarios
- **Examples:** Pricing assumptions, occupancy caps, promotional calendars

**Current state:** Empty (to be populated when parameterization is added)

---

### `processed/` - Derived Datasets
**Purpose:** Store intermediate datasets generated by data processing code  
**Characteristics:**
- **Reproducible** - Can be regenerated from raw data + code
- **Timestamped** - Indicates when processing occurred
- **Performance optimization** - Avoid re-computing daily aggregations
- **Debug-friendly** - Inspect pipeline outputs at each stage

**Current state:** Empty (pipeline currently processes in-memory)

---

### `outputs/` - Final Forecasts and Results
**Purpose:** Store model predictions and evaluation metrics  
**Characteristics:**
- **Timestamped with precision** - Date + time to avoid overwrites
- **Audit trail** - Historical record of all forecasts generated
- **Multiple formats** - CSV for data, JSON for metadata
- **User-facing** - Downloadable reports (future feature)

**Current state:** Empty (forecasts currently only displayed in browser)

---

## 6. Data Governance Rules

### Rule 1: Immutability of Historical Data
- ✅ **DO:** Upload new historical files with unique timestamps
- ✅ **DO:** Append new bookings to cumulative datasets
- ❌ **DON'T:** Edit or overwrite existing raw files in `historical/`
- ❌ **DON'T:** Delete historical files without backup

**Enforcement:** Consider file permissions (read-only after upload)

---

### Rule 2: Reproducibility of Processed Data
- ✅ **DO:** Document code version used to generate processed files
- ✅ **DO:** Include processing timestamp in filename
- ✅ **DO:** Delete and regenerate processed files when raw data changes
- ❌ **DON'T:** Manually edit processed files
- ❌ **DON'T:** Use processed files as inputs to other processing (chain back to raw)

**Enforcement:** Add processing metadata (git commit hash, dependencies) to file headers

---

### Rule 3: Calendar Data is Shared State
- ✅ **DO:** Treat `calendar/` files as read-only by application code
- ✅ **DO:** Update calendar files manually when official calendars change
- ✅ **DO:** Track calendar files in git (they're small and stable)
- ❌ **DON'T:** Generate or modify calendar files programmatically
- ❌ **DON'T:** Mix calendar data with historical bookings

**Enforcement:** Calendar files have official year ranges - don't create overlapping files

---

### Rule 4: Parameters Must Be Explicit and Auditable
- ✅ **DO:** Use CSV for parameters (human-readable, diff-friendly)
- ✅ **DO:** Create new parameter files for experiments (don't overwrite defaults)
- ✅ **DO:** Link forecasts to parameter files used (metadata)
- ❌ **DON'T:** Hardcode assumptions in Python code
- ❌ **DON'T:** Mix parameters with historical data

**Enforcement:** Parameter files must validate against a schema (future improvement)

---

### Rule 5: Outputs Must Be Timestamped and Traceable
- ✅ **DO:** Include full timestamp (YYYYMMDD_HHMMSS) in output filenames
- ✅ **DO:** Save metadata alongside forecasts (model version, inputs used)
- ✅ **DO:** Keep outputs indefinitely (disk is cheap, reproducibility is hard)
- ❌ **DON'T:** Overwrite previous forecasts
- ❌ **DON'T:** Save outputs without accompanying metadata

**Enforcement:** Create paired files: `forecast_*.csv` + `forecast_*_meta.json`

---

### Rule 6: Naming Conventions Are Strict
- ✅ **DO:** Follow the formats defined in Section 4
- ✅ **DO:** Use lowercase and underscores only
- ✅ **DO:** Make filenames self-documenting (avoid abbreviations)
- ❌ **DON'T:** Use spaces, uppercase, or special characters
- ❌ **DON'T:** Use generic names like `data.csv` or `output.csv`

**Enforcement:** Add filename validation in upload routes

---

## 7. Gaps Identified (Based on Audit)

### Current Gaps from docs/repo_state_audit.md:

1. **Orphaned calendar data**
   - `holidays_cl_2022_2040.csv` and `special_days_cl_2022_2040.csv` exist but are never loaded
   - No code integrates holiday effects into forecasting model
   - **Impact:** Missing opportunity to model seasonality based on official holidays

2. **No processed data layer**
   - Daily aggregations computed in-memory during each request
   - No persistence of intermediate transformations
   - **Impact:** Slow response times, no ability to inspect pipeline outputs

3. **No output persistence**
   - Forecasts displayed in browser but never saved to disk
   - No audit trail of predictions made
   - **Impact:** Cannot compare forecast accuracy over time, no downloadable reports

4. **No naming standards enforced**
   - Current file: `CONSOLIDADO REFUGIO.csv` (spaces, uppercase, no versioning)
   - **Impact:** Difficult to programmatically discover files, unclear provenance

5. **No data validation**
   - No schema enforcement on CSV uploads
   - No checks for required columns, date formats, or value ranges
   - **Impact:** Runtime errors when processing malformed CSVs

6. **No model artifacts saved**
   - Despite `save_model()` function existing, `models/` folder is empty
   - **Impact:** Every forecast requires re-training (slow, non-deterministic)

---

## 8. Minimal Next Steps

### Step 1: Create Folder Structure
```bash
mkdir data\historical
mkdir data\calendar
mkdir data\parameters
mkdir data\processed
mkdir data\outputs
```

### Step 2: Migrate Existing Files
```bash
# Move and rename historical data
move data\CONSOLIDADO REFUGIO.csv data\historical\bookings_raw_20220415_20251229.csv

# Move calendar files
move data\holidays_cl_2022_2040.csv data\calendar\
move data\special_days_cl_2022_2040.csv data\calendar\
```

### Step 3: Update `.gitignore`
```diff
- data/*.csv
- !data/sample_bookings.csv
+ data/historical/*.csv
+ data/processed/*.csv
+ data/outputs/*.csv
+ !data/historical/bookings_raw_20220415_20251229.csv
```

### Step 4: Update Application Code
- Modify `app/__init__.py` to create subfolders on startup
- Update `app/routes.py` to save uploads to `data/historical/`
- Add filename validation to enforce naming conventions

### Step 5: Document Active Datasets
Create `data/README.md`:
```markdown
# Data Folder Overview

## Active Datasets
- `historical/bookings_raw_20220415_20251229.csv` - Historical bookings (133 records)
- `calendar/holidays_cl_2022_2040.csv` - Chilean public holidays (2022-2040)
- `calendar/special_days_cl_2022_2040.csv` - Holidays + sandwich days (2022-2040)

## Folder Purposes
See: docs/data_folder_standard.md
```

---

## Migration Checklist

- [ ] Create 5 subfolders under `data/`
- [ ] Move and rename `CONSOLIDADO REFUGIO.csv`
- [ ] Move holiday files to `calendar/`
- [ ] Update `.gitignore` rules
- [ ] Update `app/__init__.py` (create subfolders)
- [ ] Update `app/routes.py` (upload path)
- [ ] Create `data/README.md`
- [ ] Test upload/forecast flow with new structure
- [ ] Commit changes: "Implement standardized data folder structure"

---

**End of Document**
