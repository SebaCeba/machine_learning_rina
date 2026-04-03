import pandas as pd
from datetime import datetime, timedelta

def parse_csv(filepath):
    """
    Parse CSV file and extract required fields.
    Expected columns: check_in, check_out, noches, ingresos_total
    Supports both comma (,) and semicolon (;) separators.
    Supports multiple date formats.
    """
    # Try to detect separator
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        first_line = f.readline()
        separator = ';' if ';' in first_line else ','
    
    # Read CSV with detected separator and encoding
    df = pd.read_csv(filepath, sep=separator, encoding='utf-8-sig')
    
    # Validate required columns
    required_cols = ['check_in', 'check_out', 'noches', 'ingresos_total']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Convert dates - try multiple formats
    date_formats = ['%d-%m-%Y', '%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y']
    for col in ['check_in', 'check_out']:
        df[col] = pd.to_datetime(df[col], format='mixed', dayfirst=True, errors='coerce')
    
    # Remove rows with invalid dates
    df = df.dropna(subset=['check_in', 'check_out'])
    
    # Ensure noches is numeric
    df['noches'] = pd.to_numeric(df['noches'], errors='coerce')
    df['ingresos_total'] = pd.to_numeric(df['ingresos_total'], errors='coerce')
    
    # Remove rows with invalid numeric data
    df = df.dropna(subset=['noches', 'ingresos_total'])
    
    return df

def convert_to_daily_timeseries(df):
    """
    Convert booking data into daily time series (date, revenue).
    Distribute revenue across the nights stayed.
    Treats noches=0 as cancellations (excluded from forecast).
    """
    daily_data = []
    skipped_records = 0
    cancellations = 0
    
    for _, row in df.iterrows():
        check_in = row['check_in']
        check_out = row['check_out']
        total_revenue = row['ingresos_total']
        noches = row['noches']
        
        # Skip invalid records
        if pd.isna(total_revenue) or total_revenue <= 0:
            skipped_records += 1
            continue
        
        # Treat noches=0 as cancellations - exclude from analysis
        if noches <= 0:
            cancellations += 1
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
        raise ValueError(f"No valid data to process. {cancellations} cancellations, {skipped_records} invalid records.")
    
    # Group by date and sum revenue
    daily_aggregated = daily_df.groupby('date')['revenue'].sum().reset_index()
    daily_aggregated.columns = ['ds', 'y']  # Prophet naming convention
    
    print(f"✓ Processed {len(daily_df)} daily records from {len(df)} bookings")
    print(f"✗ Excluded: {cancellations} cancellations, {skipped_records} invalid records")
    
    return daily_aggregated
