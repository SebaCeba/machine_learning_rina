import pickle
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

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
