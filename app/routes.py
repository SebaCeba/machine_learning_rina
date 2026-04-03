from flask import Blueprint, render_template, request, current_app
import os
from datetime import datetime
from app.data_loader import parse_csv, convert_to_daily_timeseries
from app.model import train_forecast_model, save_model

bp = Blueprint('main', __name__)

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            return render_template('index.html', error='No file uploaded')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template('index.html', error='No file selected')
        
        if not file.filename.endswith('.csv'):
            return render_template('index.html', error='File must be a CSV')
        
        try:
            # Save uploaded file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'bookings_{timestamp}.csv'
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse CSV
            df = parse_csv(filepath)
            
            # Convert to daily time series
            daily_data = convert_to_daily_timeseries(df)
            
            # Train model and forecast
            results = train_forecast_model(daily_data, periods=30)
            
            # Save model
            model_filename = f'forecast_model_{timestamp}.pkl'
            model_path = os.path.join(current_app.config['MODEL_FOLDER'], model_filename)
            save_model(results['model'], model_path)
            
            # Prepare forecast data for display
            forecast_df = results['forecast']
            
            # Get only future predictions (last 30 days)
            future_forecast = forecast_df.tail(30)
            
            # Prepare historical data
            historical = results['historical'].tail(30)  # Last 30 days of historical
            
            # Convert to list of dicts for template
            forecast_data = future_forecast.to_dict('records')
            historical_data = historical.to_dict('records')
            
            return render_template(
                'index.html',
                forecast=forecast_data,
                historical=historical_data,
                model_saved=model_filename,
                success=True
            )
            
        except Exception as e:
            return render_template('index.html', error=f'Error processing file: {str(e)}')
    
    return render_template('index.html')
