# Daily Occupancy Transformation Logic
**Date:** 2026-04-03  
**Repository:** machine_learning_rina  
**Function:** `transform_bookings_to_daily_occupancy()`

---

## 1. Purpose

Transform booking-level data (check-in/check-out records) into a daily occupancy time series suitable for forecasting. The output is a binary indicator (1 = occupied, 0 = free) for each day in the historical range.

---

## 2. Input File

**File:** `data/CONSOLIDADO REFUGIO.csv`  
**Format:** Semicolon-delimited CSV  
**Encoding:** UTF-8-BOM (supports Spanish characters)  
**Records:** 137 bookings (as of 2026-04-03)

---

## 3. Input Columns Used

| Column | Type | Description | Usage |
|--------|------|-------------|-------|
| `check_in` | Date | Guest arrival date | Start of occupied period |
| `check_out` | Date | Guest departure date | **NOT counted** as occupied night |
| `noches` | Integer | Number of nights stayed | Determines occupied nights count |
| `ingresos_total` | Float | Total revenue (NOT used in occupancy) | Ignored for binary occupancy |

**Date formats supported:** DD-MM-YYYY, YYYY-MM-DD, mixed formats via pandas `format='mixed', dayfirst=True`

---

## 4. Occupancy Logic

### Core Rule:
**Each booking occupies `noches` consecutive nights starting from `check_in`.**

### Example:
```
Booking:
  check_in: 2024-01-15
  check_out: 2024-01-18
  noches: 3

Occupied nights:
  2024-01-15 → y=1
  2024-01-16 → y=1
  2024-01-17 → y=1
  2024-01-18 → y=0  (check_out NOT occupied)
```

### Transformation Steps:

1. **Parse bookings** - Read raw CSV, validate columns, parse dates
2. **Exclude cancellations** - Remove bookings where `noches = 0`
3. **Expand bookings** - For each booking, create one row per occupied night:
   - Start from `check_in`
   - Generate `noches` consecutive dates
   - Each date gets `y=1` (occupied)
4. **Handle overlaps** - If multiple bookings occupy same night, keep `y=1` (max aggregation)
5. **Create complete date range** - Generate all dates from min occupied date to max occupied date
6. **Fill gaps** - Dates with no bookings get `y=0` (free)
7. **Export** - Save to `data/processed/bookings_daily_occupancy_YYYYMMDD.csv`

---

## 5. Why check_out is Excluded

**Reason:** Hotel/refuge industry standard - guests depart on check-out day, making the room available for new arrivals.

**Business logic:**
- `check_in = 2024-01-15, check_out = 2024-01-18, noches = 3`
- Guest occupies: Jan 15, 16, 17 (3 nights)
- Guest departs: Jan 18 (morning departure, room available for cleaning and new booking)

**Mathematical consistency:**
- `noches = (check_out - check_in).days` → Matches booking record
- Counting `check_out` would create `noches + 1` occupied nights → Incorrect

---

## 6. Cancellation Handling

**Rule:** Bookings with `noches = 0` are treated as cancellations and **excluded** from occupancy calculations.

**Rationale:**
- `noches = 0` means no nights stayed (booking was canceled or no-show)
- Including these would create division-by-zero errors in revenue distribution
- They do not represent actual refuge usage

**Implementation:**
```python
if noches <= 0:
    cancellations += 1
    continue  # Skip this booking
```

**Example from CONSOLIDADO REFUGIO.csv:**
- Total bookings: 137
- Cancellations (noches=0): 4
- Valid bookings: 133

---

## 7. Output Schema

### Columns:

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `ds` | Date | Date (Prophet naming convention) | YYYY-MM-DD |
| `y` | Integer | Occupancy indicator | 1 = occupied, 0 = free |

### Properties:

- **Complete date range** - No missing dates between min and max
- **Binary values** - Only 0 or 1 (never fractional)
- **No duplicates** - One row per date
- **Column names** - Prophet convention (`ds`, `y`) for future model compatibility

### Example Output:

```csv
ds,y
2022-04-15,1
2022-04-16,0
2022-04-17,1
2022-04-18,1
2022-04-19,0
...
```

---

## 8. Output File Location

**Path:** `data/processed/bookings_daily_occupancy_YYYYMMDD.csv`

**Example:** `data/processed/bookings_daily_occupancy_20260403.csv`

**Naming convention:**
- `bookings_` - Content type (booking-derived)
- `daily_` - Granularity (daily aggregation)
- `occupancy_` - Metric type (binary occupancy)
- `YYYYMMDD` - Processing date (when file was created)

**Reproducibility:**
- File can be regenerated from raw data + code
- Timestamp indicates when processing occurred
- Multiple versions can coexist for comparison

---

## 9. Usage Example

```python
from app.data_loader import transform_bookings_to_daily_occupancy

# Transform raw bookings to daily occupancy
daily_occupancy = transform_bookings_to_daily_occupancy(
    filepath='data/CONSOLIDADO REFUGIO.csv',
    output_dir='data/processed'
)

# Output:
# ✓ Created daily occupancy dataset: bookings_daily_occupancy_20260403.csv
#   Date range: 2022-04-15 to 2025-12-29
#   Total days: 1354
#   Occupied: 615 (45.4%)
#   Free: 739 (54.6%)
#   Excluded: 4 cancellations
#   Saved to: data/processed/bookings_daily_occupancy_20260403.csv

# Result is a DataFrame with columns: ['ds', 'y']
print(daily_occupancy.head())
#           ds  y
# 0 2022-04-15  1
# 1 2022-04-16  0
# 2 2022-04-17  1
# 3 2022-04-18  1
# 4 2022-04-19  0
```

---

## 10. Related Documentation

- **Data folder structure:** See `docs/data_folder_standard.md`
- **Repository audit:** See `docs/repo_state_audit.md`
- **Raw data source:** `data/CONSOLIDADO REFUGIO.csv`
- **Processing code:** `app/data_loader.py::transform_bookings_to_daily_occupancy()`

---

**End of Document**
