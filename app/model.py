import pickle
from prophet import Prophet
import pandas as pd

def train_forecast_model(daily_data, periods=30):
    """
    Train a Prophet model and generate forecast.
    
    Args:
        daily_data: DataFrame with columns 'ds' (date) and 'y' (revenue)
        periods: Number of days to forecast
    
    Returns:
        dict with 'model', 'forecast', 'historical'
    """
    # Initialize and train Prophet model
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.05
    )
    
    model.fit(daily_data)
    
    # Create future dataframe
    future = model.make_future_dataframe(periods=periods)
    
    # Generate forecast
    forecast = model.predict(future)
    
    # Prepare results
    results = {
        'model': model,
        'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
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
