from flask import Blueprint, render_template, request, current_app
import os
import pandas as pd
from datetime import datetime
from app.data_loader import parse_csv, transform_bookings_to_daily_occupancy, enrich_daily_occupancy_with_calendar
from app.model import train_and_forecast_sarimax, save_model

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
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f'bookings_{timestamp}.csv'
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Parse CSV
            df = parse_csv(filepath)
            
            # Transform bookings to daily occupancy
            occupancy_filepath = os.path.join('data/processed', f'bookings_daily_occupancy_{timestamp}.csv')
            daily_occupancy = transform_bookings_to_daily_occupancy(df, output_filepath=occupancy_filepath)
            
            # Enrich with Chilean calendar context
            features_filepath = os.path.join('data/processed', f'features_daily_{timestamp}.csv')
            calendar_filepath = 'data/special_days_cl_2022_2040.csv'
            enriched_data = enrich_daily_occupancy_with_calendar(
                daily_occupancy_filepath=occupancy_filepath,
                calendar_filepath=calendar_filepath,
                output_filepath=features_filepath
            )
            
            # Train SARIMAX model and forecast 60 days
            forecast_df = train_and_forecast_sarimax(
                features_filepath=features_filepath,
                forecast_horizon=60,
                output_dir='data/outputs'
            )
            
            # Prepare historical data (last 30 days)
            historical = enriched_data.tail(30)
            
            # Convert to list of dicts for template
            forecast_data = forecast_df.to_dict('records')
            historical_data = historical.to_dict('records')
            
            # Statistics for display
            total_days = len(enriched_data)
            occupied_days = int(enriched_data['y'].sum())
            occupancy_rate = (occupied_days / total_days * 100) if total_days > 0 else 0
            avg_forecast_occupancy = forecast_df['yhat'].mean() * 100
            
            return render_template(
                'index.html',
                forecast=forecast_data,
                historical=historical_data,
                total_days=total_days,
                occupied_days=occupied_days,
                occupancy_rate=occupancy_rate,
                avg_forecast_occupancy=avg_forecast_occupancy,
                forecast_days=len(forecast_df),
                success=True
            )
            
        except Exception as e:
            return render_template('index.html', error=f'Error processing file: {str(e)}')
    
    return render_template('index.html')
