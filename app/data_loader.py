import pandas as pd
from datetime import datetime, timedelta

def parse_csv(filepath):
    """
    Parse CSV file and extract required fields.
    Expected columns: check_in, check_out, noches, ingresos_total
    """
    df = pd.read_csv(filepath)
    
    # Validate required columns
    required_cols = ['check_in', 'check_out', 'noches', 'ingresos_total']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Convert dates
    df['check_in'] = pd.to_datetime(df['check_in'])
    df['check_out'] = pd.to_datetime(df['check_out'])
    
    return df

def convert_to_daily_timeseries(df):
    """
    Convert booking data into daily time series (date, revenue).
    Distribute revenue across the nights stayed.
    """
    daily_data = []
    
    for _, row in df.iterrows():
        check_in = row['check_in']
        check_out = row['check_out']
        total_revenue = row['ingresos_total']
        noches = row['noches']
        
        # Skip invalid records
        if noches <= 0 or pd.isna(total_revenue):
            continue
        
        # Distribute revenue per night
        revenue_per_night = total_revenue / noches
        
        # Generate dates for each night
        current_date = check_in
        for _ in range(int(noches)):
            daily_data.append({
                'date': current_date,
                'revenue': revenue_per_night
            })
            current_date += timedelta(days=1)
    
    # Create DataFrame and aggregate by date
    daily_df = pd.DataFrame(daily_data)
    
    if daily_df.empty:
        raise ValueError("No valid data to process")
    
    # Group by date and sum revenue
    daily_aggregated = daily_df.groupby('date')['revenue'].sum().reset_index()
    daily_aggregated.columns = ['ds', 'y']  # Prophet naming convention
    
    return daily_aggregated
