import pickle
import pandas as pd
import numpy as np
import os
from datetime import datetime
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except (ImportError, AttributeError) as e:
    PROPHET_AVAILABLE = False
    Prophet = None

def train_forecast_model(daily_data, periods=30):
    """
    Train a Holt-Winters model and generate forecast.
    
    Args:
        daily_data: DataFrame with columns 'ds' (date) and 'y' (revenue)
        periods: Number of days to forecast
    
    Returns:
        dict with 'model', 'forecast', 'historical'
    """
    # Prepare data
    ts_data = daily_data.set_index('ds')['y']
    
    # Fill any missing dates with forward fill
    ts_data = ts_data.asfreq('D', method='ffill')
    
    # Train Holt-Winters model
    try:
        model = ExponentialSmoothing(
            ts_data,
            seasonal_periods=7,  # Weekly seasonality
            trend='add',
            seasonal='add'
        )
        fitted_model = model.fit()
    except:
        # Fallback to simpler model if seasonal doesn't work
        model = ExponentialSmoothing(
            ts_data,
            trend='add',
            seasonal=None
        )
        fitted_model = model.fit()
    
    # Generate forecast
    forecast_values = fitted_model.forecast(steps=periods)
    
    # Create forecast dataframe
    last_date = daily_data['ds'].max()
    forecast_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=periods,
        freq='D'
    )
    
    forecast_df = pd.DataFrame({
        'ds': forecast_dates,
        'yhat': forecast_values.values,
        'yhat_lower': forecast_values.values * 0.9,  # Simple confidence interval
        'yhat_upper': forecast_values.values * 1.1
    })
    
    # Prepare results
    results = {
        'model': fitted_model,
        'forecast': forecast_df,
        'historical': daily_data
    }
    
    return results

def save_model(model, filepath):
    """Save trained model to disk."""
    with open(filepath, 'wb') as f:
        pickle.dump(model, f)

def load_model(filepath):
    """Load trained model from disk."""
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def train_and_forecast_occupancy(
    features_filepath=None,
    features_df=None,
    forecast_horizon=60,
    output_dir='data/outputs'
):
    """
    Train a Prophet model on daily occupancy data with Chilean calendar features.
    
    Args:
        features_filepath (str): Path to features CSV (optional if features_df provided)
        features_df (pd.DataFrame): Features dataframe (optional if features_filepath provided)
        forecast_horizon (int): Number of days to forecast (default: 60)
        output_dir (str): Directory to save forecast output (default: 'data/outputs')
    
    Returns:
        dict: {
            'model': Trained Prophet model,
            'forecast': Forecast dataframe with predictions,
            'historical': Historical data used for training
        }
    
    Features used as regressors:
        - is_holiday: Official Chilean public holidays
        - is_sandwich: Sandwich days (behavioral bridge days)
        - is_weekend: Saturday/Sunday indicator
    
    Output columns:
        - ds: Date
        - yhat: Predicted occupancy
        - yhat_lower: Lower bound of prediction interval
        - yhat_upper: Upper bound of prediction interval
        - is_holiday, is_sandwich, is_weekend: Future regressor values
    
    Saves forecast to: {output_dir}/forecast_occupancy_YYYYMMDD.csv
    """
    # Load features data
    if features_df is not None:
        df = features_df.copy()
    elif features_filepath is not None:
        df = pd.read_csv(features_filepath)
        df['ds'] = pd.to_datetime(df['ds'])
    else:
        raise ValueError("Must provide either features_filepath or features_df")
    
    # Validate required columns
    required_cols = ['ds', 'y', 'is_holiday', 'is_sandwich', 'is_weekend']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Features dataset missing required columns: {missing}")
    
    # Check if Prophet is available
    if not PROPHET_AVAILABLE:
        raise ImportError(
            "Prophet library is not installed or failed to import. "
            "\nOn Windows, Prophet installs but requires cmdstan backend (C++ compilation)."
            "\nCurrent system lacks MinGW or Visual Studio Build Tools needed for cmdstan."
            "\n\nSolutions:"
            "\n1. Use SARIMAX alternative (see docs/model_training.md Section 8, Option 2)"
            "\n2. Run in Docker with Linux container"
            "\n3. Use cloud deployment (Linux VM)"
            "\n4. Install MinGW: https://www.mingw-w64.org/ (requires ~5GB + configuration)"
        )
    
    # Prepare training data (Prophet requires 'ds' and 'y')
    train_df = df[['ds', 'y', 'is_holiday', 'is_sandwich', 'is_weekend']].copy()
    
    # Initialize Prophet model
    print(f"Training Prophet model on {len(train_df)} days of data...")
    try:
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode='additive',
            interval_width=0.95  # 95% confidence intervals
        )
    except AttributeError as e:
        raise RuntimeError(
            f"Prophet initialization failed: {e}"
            "\n\nROOT CAUSE: cmdstan backend is not installed/compiled."
            "\nProphet library is installed but cannot run without cmdstan."
            "\n\nWhy cmdstan failed:"
            "\n- Command 'mingw32-make' not found on Windows system"
            "\n- Requires MinGW (gcc/g++/make) or Visual Studio Build Tools"
            "\n\nQuick fix options:"
            "\n1. RECOMMENDED: Use SARIMAX instead (works on Windows, supports regressors)"
            "\n   See docs/model_training.md Section 8, Option 2"
            "\n2. Install MinGW-w64 from https://www.mingw-w64.org/ then run:"
            "\n   python -c 'import cmdstanpy; cmdstanpy.install_cmdstan()'"
            "\n3. Use Docker (Prophet works in Linux containers)"
            "\n\nFor detailed troubleshooting: docs/model_training.md"
        )
    
    # Add external regressors
    model.add_regressor('is_holiday')
    model.add_regressor('is_sandwich')
    model.add_regressor('is_weekend')
    
    # Fit model
    print(f"Training Prophet model on {len(train_df)} days of data...")
    model.fit(train_df)
    print(f"✓ Model training complete")
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=forecast_horizon, freq='D')
    
    # Add regressors to future dataframe
    # For future dates, we need to populate regressor values
    future['day_of_week'] = future['ds'].dt.dayofweek
    future['is_weekend'] = future['day_of_week'].isin([5, 6]).astype(int)
    
    # Load calendar data for future holiday/sandwich values
    try:
        calendar_df = None
        calendar_path = 'data/special_days_cl_2022_2040.csv'
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                calendar_df = pd.read_csv(calendar_path, encoding=encoding)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if calendar_df is not None:
            calendar_df['date'] = pd.to_datetime(calendar_df['date'])
            calendar_df = calendar_df[['date', 'is_public_holiday', 'is_sandwich']].copy()
            calendar_df.columns = ['ds', 'is_holiday', 'is_sandwich']
            
            # Merge future with calendar
            future = future.merge(calendar_df, on='ds', how='left')
        else:
            future['is_holiday'] = 0
            future['is_sandwich'] = 0
    except FileNotFoundError:
        # No calendar file, default to 0
        future['is_holiday'] = 0
        future['is_sandwich'] = 0
    
    # Fill any missing regressor values with 0
    future['is_holiday'] = future['is_holiday'].fillna(0).astype(int)
    future['is_sandwich'] = future['is_sandwich'].fillna(0).astype(int)
    
    # Generate forecast
    print(f"Generating {forecast_horizon}-day forecast...")
    forecast = model.predict(future)
    
    # Extract forecast period only (exclude historical fit)
    last_historical_date = train_df['ds'].max()
    forecast_only = forecast[forecast['ds'] > last_historical_date].copy()
    
    # Select relevant columns for output
    output_cols = ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    forecast_output = forecast_only[output_cols].copy()
    
    # Add regressor values to output for transparency
    future_regressors = future[future['ds'] > last_historical_date][['ds', 'is_holiday', 'is_sandwich', 'is_weekend']].copy()
    forecast_output = forecast_output.merge(future_regressors, on='ds', how='left')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    output_filename = f'forecast_occupancy_{timestamp}.csv'
    output_path = os.path.join(output_dir, output_filename)
    
    # Save forecast to CSV
    forecast_output.to_csv(output_path, index=False)
    
    # Summary statistics
    avg_prediction = forecast_output['yhat'].mean()
    min_prediction = forecast_output['yhat'].min()
    max_prediction = forecast_output['yhat'].max()
    
    print(f"✓ Forecast saved: {output_filename}")
    print(f"  Forecast period: {forecast_output['ds'].min().date()} to {forecast_output['ds'].max().date()}")
    print(f"  Total days forecasted: {len(forecast_output)}")
    print(f"  Average predicted occupancy: {avg_prediction:.3f}")
    print(f"  Range: [{min_prediction:.3f}, {max_prediction:.3f}]")
    print(f"  Saved to: {output_path}")
    
    # Prepare results
    results = {
        'model': model,
        'forecast': forecast_output,
        'historical': train_df
    }
    
    return results


def train_and_forecast_sarimax(
    features_filepath=None,
    features_df=None,
    forecast_horizon=60,
    output_dir='data/outputs'
):
    """
    Train a SARIMAX model on daily occupancy data with Chilean calendar features.
    WINDOWS-COMPATIBLE alternative to Prophet.
    
    SARIMAX (Seasonal ARIMA with eXogenous variables) supports external regressors
    like Prophet but works on Windows without C++ compilation requirements.
    
    Args:
        features_filepath (str): Path to features CSV (optional if features_df provided)
        features_df (pd.DataFrame): Features dataframe (optional if features_filepath provided)
        forecast_horizon (int): Number of days to forecast (default: 60)
        output_dir (str): Directory to save forecast output (default: 'data/outputs')
    
    Returns:
        dict: {
            'model': Trained SARIMAX model,
            'forecast': Forecast dataframe with predictions,
            'historical': Historical data used for training
        }
    
    Features used as exogenous variables:
        - is_holiday: Official Chilean public holidays
        - is_sandwich: Sandwich days (behavioral bridge days)
        - is_weekend: Saturday/Sunday indicator
    
    Model specification:
        - order=(1, 0, 1): ARMA(1,1) for non-seasonal component
        - seasonal_order=(1, 0, 1, 7): Seasonal ARMA(1,1) with 7-day period (weekly)
        - exog: External regressors (holidays, sandwiches, weekends)
    
    Output columns:
        - ds: Date
        - yhat: Predicted occupancy
        - yhat_lower: Lower bound of prediction interval
        - yhat_upper: Upper bound of prediction interval
        - is_holiday, is_sandwich, is_weekend: Future regressor values
    
    Saves forecast to: {output_dir}/forecast_occupancy_sarimax_YYYYMMDD.csv
    """
    # Load features data
    if features_df is not None:
        df = features_df.copy()
    elif features_filepath is not None:
        df = pd.read_csv(features_filepath)
        df['ds'] = pd.to_datetime(df['ds'])
    else:
        raise ValueError("Must provide either features_filepath or features_df")
    
    # Validate required columns
    required_cols = ['ds', 'y', 'is_holiday', 'is_sandwich', 'is_weekend']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Features dataset missing required columns: {missing}")
    
    # Prepare training data
    train_df = df[['ds', 'y', 'is_holiday', 'is_sandwich', 'is_weekend']].copy()
    train_df = train_df.sort_values('ds').reset_index(drop=True)
    
    # Prepare endogenous (y) and exogenous (regressors) variables
    endog = train_df['y'].values
    exog = train_df[['is_holiday', 'is_sandwich', 'is_weekend']].values
    
    # Initialize SARIMAX model
    print(f"Training SARIMAX model on {len(train_df)} days of data...")
    print("  Model: SARIMAX(1,0,1)x(1,0,1,7) with external regressors")
    print("  Regressors: is_holiday, is_sandwich, is_weekend")
    
    try:
        model = SARIMAX(
            endog=endog,
            exog=exog,
            order=(1, 0, 1),              # (p, d, q) - ARMA(1,1) non-seasonal
            seasonal_order=(1, 0, 1, 7),  # (P, D, Q, s) - Weekly seasonal ARMA(1,1)
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        fitted_model = model.fit(disp=False)
        print(f"✓ Model training complete (AIC: {fitted_model.aic:.2f})")
        
    except Exception as e:
        # Fallback to simpler model if seasonal doesn't converge
        print(f"⚠ Seasonal model failed ({e}), falling back to non-seasonal ARIMA")
        model = SARIMAX(
            endog=endog,
            exog=exog,
            order=(1, 0, 1),
            seasonal_order=(0, 0, 0, 0),
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        fitted_model = model.fit(disp=False)
        print(f"✓ Model training complete (AIC: {fitted_model.aic:.2f})")
    
    # Prepare future exogenous variables
    last_date = train_df['ds'].max()
    future_dates = pd.date_range(
        start=last_date + pd.Timedelta(days=1),
        periods=forecast_horizon,
        freq='D'
    )
    
    # Create future dataframe with dates
    future_df = pd.DataFrame({'ds': future_dates})
    
    # Add weekend indicator (derived from date)
    future_df['day_of_week'] = future_df['ds'].dt.dayofweek
    future_df['is_weekend'] = future_df['day_of_week'].isin([5, 6]).astype(int)
    
    # Load calendar data for future holiday/sandwich values
    try:
        calendar_df = None
        calendar_path = 'data/special_days_cl_2022_2040.csv'
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                calendar_df = pd.read_csv(calendar_path, encoding=encoding)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if calendar_df is not None:
            calendar_df['date'] = pd.to_datetime(calendar_df['date'])
            calendar_df = calendar_df[['date', 'is_public_holiday', 'is_sandwich']].copy()
            calendar_df.columns = ['ds', 'is_holiday', 'is_sandwich']
            
            # Merge future with calendar
            future_df = future_df.merge(calendar_df, on='ds', how='left')
        else:
            future_df['is_holiday'] = 0
            future_df['is_sandwich'] = 0
    except FileNotFoundError:
        future_df['is_holiday'] = 0
        future_df['is_sandwich'] = 0
    
    # Fill any missing regressor values with 0
    future_df['is_holiday'] = future_df['is_holiday'].fillna(0).astype(int)
    future_df['is_sandwich'] = future_df['is_sandwich'].fillna(0).astype(int)
    
    # Prepare exogenous variables for forecast
    future_exog = future_df[['is_holiday', 'is_sandwich', 'is_weekend']].values
    
    # Generate forecast
    print(f"Generating {forecast_horizon}-day forecast...")
    forecast_result = fitted_model.get_forecast(steps=forecast_horizon, exog=future_exog)
    
    # Extract predictions and confidence intervals
    forecast_mean = forecast_result.predicted_mean
    forecast_ci = forecast_result.conf_int(alpha=0.05)  # 95% confidence interval
    
    # Create forecast dataframe
    forecast_output = pd.DataFrame({
        'ds': future_dates,
        'yhat': forecast_mean,
        'yhat_lower': forecast_ci[:, 0] if isinstance(forecast_ci, np.ndarray) else forecast_ci.iloc[:, 0],
        'yhat_upper': forecast_ci[:, 1] if isinstance(forecast_ci, np.ndarray) else forecast_ci.iloc[:, 1]
    })
    
    # Add regressor values to output for transparency
    forecast_output = forecast_output.merge(
        future_df[['ds', 'is_holiday', 'is_sandwich', 'is_weekend']], 
        on='ds', 
        how='left'
    )
    
    # Clip predictions to valid range [0, 1] for occupancy probability
    forecast_output['yhat'] = forecast_output['yhat'].clip(0, 1)
    forecast_output['yhat_lower'] = forecast_output['yhat_lower'].clip(0, 1)
    forecast_output['yhat_upper'] = forecast_output['yhat_upper'].clip(0, 1)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    output_filename = f'forecast_occupancy_sarimax_{timestamp}.csv'
    output_path = os.path.join(output_dir, output_filename)
    
    # Save forecast to CSV
    forecast_output.to_csv(output_path, index=False)
    
    # Summary statistics
    avg_prediction = forecast_output['yhat'].mean()
    min_prediction = forecast_output['yhat'].min()
    max_prediction = forecast_output['yhat'].max()
    holidays_in_forecast = forecast_output['is_holiday'].sum()
    sandwiches_in_forecast = forecast_output['is_sandwich'].sum()
    weekends_in_forecast = forecast_output['is_weekend'].sum()
    
    print(f"✓ Forecast saved: {output_filename}")
    print(f"  Forecast period: {forecast_output['ds'].min().date()} to {forecast_output['ds'].max().date()}")
    print(f"  Total days forecasted: {len(forecast_output)}")
    print(f"  Average predicted occupancy: {avg_prediction:.3f}")
    print(f"  Range: [{min_prediction:.3f}, {max_prediction:.3f}]")
    print(f"  Calendar features in forecast period:")
    print(f"    Holidays: {holidays_in_forecast}")
    print(f"    Sandwich days: {sandwiches_in_forecast}")
    print(f"    Weekends: {weekends_in_forecast}")
    print(f"  Saved to: {output_path}")
    
    # Prepare results
    results = {
        'model': fitted_model,
        'forecast': forecast_output,
        'historical': train_df,
        'model_summary': fitted_model.summary()
    }
    
    return results
