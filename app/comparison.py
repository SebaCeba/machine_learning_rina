"""
comparison.py - Compare real booking data against a generated forecast.

Workflow:
1. Parse uploaded booking CSV (check_in, check_out, noches)
2. Expand bookings into daily actual occupancy (y_real)
3. Load latest forecast CSV from data/outputs/
4. Merge on ds, keep only overlapping dates
5. Calculate comparison metrics and save results
"""
import os
import glob
import pandas as pd
from datetime import datetime, timedelta


# ---------------------------------------------------------------------------
# Step 1 – Parse and expand uploaded bookings into daily actual occupancy
# ---------------------------------------------------------------------------

def parse_actuals_from_bookings(filepath):
    """
    Parse a booking CSV file and return a daily occupancy DataFrame with
    columns [ds, y_real].

    Accepted booking columns: check_in, check_out, noches (required)
    Date format: DD-MM-YYYY (with mixed fallback)
    Cancellations (noches <= 0 or NaN) are excluded.
    check_out date is NOT counted as an occupied night.
    If multiple bookings overlap on the same day, y_real is still 1.

    Returns:
        pd.DataFrame with columns [ds, y_real]

    Raises:
        ValueError with a descriptive message on any validation failure.
    """
    # --- detect encoding and separator ---
    encodings = ['utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    df = None
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                first_line = f.readline()
            sep = ';' if ';' in first_line else ','
            df = pd.read_csv(filepath, sep=sep, encoding=enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if df is None:
        raise ValueError("No se pudo leer el archivo con ninguna codificación admitida.")

    if df.empty:
        raise ValueError("El archivo subido está vacío.")

    # --- validate required columns ---
    required = ['check_in', 'check_out', 'noches']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Columnas requeridas faltantes: {missing}")

    # --- parse dates ---
    for col in ['check_in', 'check_out']:
        df[col] = pd.to_datetime(df[col], format='mixed', dayfirst=True, errors='coerce')

    # --- parse noches ---
    df['noches'] = pd.to_numeric(df['noches'], errors='coerce')

    # drop rows with unparseable dates
    bad_dates = df['check_in'].isna() | df['check_out'].isna()
    if bad_dates.any():
        df = df[~bad_dates]

    if df.empty:
        raise ValueError("Ninguna fila tiene fechas válidas de check_in / check_out.")

    # --- expand each booking into nightly rows ---
    occupied = set()
    cancellations = 0

    for _, row in df.iterrows():
        noches = row['noches']
        if pd.isna(noches) or noches <= 0:
            cancellations += 1
            continue
        current = row['check_in']
        for _ in range(int(noches)):
            occupied.add(current.date())
            current += timedelta(days=1)

    if not occupied:
        raise ValueError(
            f"No hay noches ocupadas válidas. "
            f"{cancellations} fila(s) excluidas (cancelaciones o noches inválidas)."
        )

    # build daily frame
    dates_sorted = sorted(occupied)
    daily_df = pd.DataFrame({'ds': pd.to_datetime(dates_sorted), 'y_real': 1})

    return daily_df


# ---------------------------------------------------------------------------
# Step 2 – Load the latest forecast CSV
# ---------------------------------------------------------------------------

def load_latest_forecast(outputs_dir='data/outputs'):
    """
    Load the most recent forecast_occupancy_sarimax_*.csv from outputs_dir.

    Returns:
        pd.DataFrame with at least [ds, yhat, yhat_lower, yhat_upper]

    Raises:
        FileNotFoundError if no forecast file is found.
    """
    pattern = os.path.join(outputs_dir, 'forecast_occupancy_sarimax_*.csv')
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(
            f"No se encontró ningún archivo de pronóstico en '{outputs_dir}'. "
            "Genera un pronóstico primero usando la sección de carga de datos históricos."
        )
    latest = files[-1]
    forecast_df = pd.read_csv(latest, parse_dates=['ds'])
    return forecast_df


# ---------------------------------------------------------------------------
# Step 3 – Merge and compute comparison metrics
# ---------------------------------------------------------------------------

def build_comparison(actuals_df, forecast_df):
    """
    Merge actual daily occupancy with forecast on ds.

    Returns:
        pd.DataFrame with columns:
            ds, y_real, yhat, yhat_lower, yhat_upper,
            yhat_binary, error, abs_error, match_binary

    Raises:
        ValueError if no overlapping dates are found.
    """
    merged = pd.merge(actuals_df, forecast_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
                      on='ds', how='inner')

    if merged.empty:
        raise ValueError(
            "No hay fechas en común entre los datos reales y el pronóstico. "
            "Verifica que el período de reservas se superponga con el período pronosticado."
        )

    merged['yhat_binary'] = (merged['yhat'] >= 0.5).astype(int)
    merged['error'] = merged['y_real'] - merged['yhat']
    merged['abs_error'] = merged['error'].abs()
    merged['match_binary'] = (merged['y_real'] == merged['yhat_binary']).astype(int)

    merged = merged.sort_values('ds').reset_index(drop=True)
    return merged


def compute_metrics(comparison_df):
    """
    Return a dict with summary metrics.
    """
    n = len(comparison_df)
    accuracy = comparison_df['match_binary'].mean() * 100
    mae = comparison_df['abs_error'].mean()
    return {
        'total_days_compared': n,
        'binary_accuracy': round(accuracy, 2),
        'mae': round(float(mae), 4),
    }


# ---------------------------------------------------------------------------
# Step 4 – Orchestrate the entire workflow
# ---------------------------------------------------------------------------

def run_comparison(booking_filepath, outputs_dir='data/outputs', processed_dir='data/processed'):
    """
    Full pipeline:
    1. Parse actuals from booking file
    2. Load latest forecast
    3. Build comparison dataset
    4. Save results
    5. Return (comparison_df, metrics_dict)

    Args:
        booking_filepath (str): Path to uploaded booking CSV
        outputs_dir (str): Directory with forecast CSVs and comparison output
        processed_dir (str): Directory for daily occupancy intermediate file

    Returns:
        (pd.DataFrame, dict): comparison DataFrame and metrics dict
    """
    # 1. parse
    actuals_df = parse_actuals_from_bookings(booking_filepath)

    # 2. load forecast
    forecast_df = load_latest_forecast(outputs_dir)

    # 3. compare
    comparison_df = build_comparison(actuals_df, forecast_df)
    metrics = compute_metrics(comparison_df)

    timestamp = datetime.now().strftime('%Y%m%d')

    # 4a. save daily actuals (optional intermediate)
    os.makedirs(processed_dir, exist_ok=True)
    actuals_path = os.path.join(processed_dir, f'actual_daily_occupancy_{timestamp}.csv')
    actuals_df.to_csv(actuals_path, index=False)

    # 4b. save comparison output
    os.makedirs(outputs_dir, exist_ok=True)
    comparison_path = os.path.join(outputs_dir, f'forecast_vs_actual_{timestamp}.csv')
    comparison_df.to_csv(comparison_path, index=False)

    print(f"✓ Comparación guardada: {comparison_path}")
    print(f"  Días comparados : {metrics['total_days_compared']}")
    print(f"  Precisión binaria: {metrics['binary_accuracy']}%")
    print(f"  MAE             : {metrics['mae']}")

    return comparison_df, metrics
