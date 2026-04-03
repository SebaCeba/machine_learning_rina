# Forecast vs Actual Comparison

## 1. Expected uploaded file format

Upload a CSV containing real booking records, in the same format used for generating the forecast.

Supported separators: `,` (comma) or `;` (semicolon).  
Supported encodings: UTF-8, UTF-8-BOM, latin-1, cp1252.

Example:

```
booking_id;fecha_reserva;check_in;check_out;noches;ingresos_total;plataforma;uso_tinaja
;;31-12-2025;03-01-2026;3;453221;Airbnb;si
;;16-01-2026;18-01-2026;2;385560;Booking;no
```

---

## 2. Required columns

| Column     | Type   | Description                              |
|------------|--------|------------------------------------------|
| `check_in` | date   | First occupied night (DD-MM-YYYY)        |
| `check_out`| date   | Departure date — **not** counted as occupied |
| `noches`   | integer| Number of nights stayed                  |

All other columns (booking_id, ingresos_total, plataforma, etc.) are accepted but ignored for the comparison.

---

## 3. How booking rows are converted into daily occupancy

Each booking row is expanded into individual nightly records:

```
for each night in range(noches):
    mark date as occupied (y_real = 1)
```

- Rows where `noches` is null, zero, or negative are treated as cancellations and excluded.
- Rows with unparseable `check_in` or `check_out` are dropped with a warning.
- If multiple bookings overlap on the same calendar date, `y_real` is still `1` (not double-counted).
- An intermediate daily occupancy file is saved to `data/processed/actual_daily_occupancy_YYYYMMDD.csv`.

---

## 4. Why check_out is excluded

`check_out` is the guest departure date. The guest does **not** stay that night, so it is not counted as an occupied night. This is consistent with how the historical data was processed during model training.

---

## 5. How comparison is performed

1. The uploaded booking file is parsed and expanded into a `[ds, y_real]` daily dataset.
2. The most recent forecast file is loaded from `data/outputs/forecast_occupancy_sarimax_*.csv`.
3. Both datasets are merged on `ds` using an **inner join** (only overlapping dates are kept).
4. If no dates overlap, a clear error is shown and no file is saved.

The resulting comparison dataset contains:

| Column         | Description                                      |
|----------------|--------------------------------------------------|
| `ds`           | Date                                             |
| `y_real`       | Actual occupancy (0 or 1)                        |
| `yhat`         | Forecast probability (0–1)                       |
| `yhat_lower`   | Lower confidence bound                           |
| `yhat_upper`   | Upper confidence bound                           |
| `yhat_binary`  | Binary prediction (1 if yhat ≥ 0.5, else 0)     |
| `error`        | `y_real − yhat`                                  |
| `abs_error`    | `|y_real − yhat|`                                |
| `match_binary` | 1 if `y_real == yhat_binary`, else 0             |

---

## 6. How binary prediction is derived from yhat

```
yhat_binary = 1  if yhat >= 0.5
yhat_binary = 0  if yhat <  0.5
```

`yhat` is a continuous probability output from the SARIMAX model. The threshold of 0.5 converts it to a binary occupancy prediction, enabling direct comparison with the binary `y_real` values.

---

## 7. Output files generated

| File                                                          | Description                                  |
|---------------------------------------------------------------|----------------------------------------------|
| `data/processed/actual_daily_occupancy_YYYYMMDD.csv`         | Expanded daily occupancy from uploaded bookings |
| `data/outputs/forecast_vs_actual_YYYYMMDD.csv`               | Full comparison dataset with all metrics columns |

---

## 8. Metrics shown in the UI

| Metric              | Formula                                              |
|---------------------|------------------------------------------------------|
| **Días Comparados** | Number of dates present in both actuals and forecast |
| **Precisión Binaria** | `mean(match_binary) × 100` — % of days correctly predicted as occupied or free |
| **MAE**             | `mean(abs_error)` — average absolute difference between `y_real` and `yhat` |

---

## Error handling

| Situation                            | Message shown                                              |
|--------------------------------------|------------------------------------------------------------|
| Missing required columns             | Lists which columns are missing                            |
| Unparseable dates                    | Rows are skipped; error if all rows fail                  |
| No valid bookings (all cancellations)| Error with cancellation count                              |
| File is empty                        | "El archivo subido está vacío."                            |
| No forecast file in data/outputs/    | Instructs user to generate a forecast first                |
| No overlapping dates                 | Explains that the booking period and forecast period must overlap |
