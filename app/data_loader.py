import pandas as pd
from datetime import datetime, timedelta
import os

def parse_csv(filepath):
    """
    Parse CSV file and extract required fields.
    Expected columns: check_in, check_out, noches, ingresos_total
    Supports both comma (,) and semicolon (;) separators.
    Supports multiple date formats.
    """
    # Try multiple encodings
    encodings = ['utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
    df = None
    separator = ';'
    
    for encoding in encodings:
        try:
            # Try to detect separator
            with open(filepath, 'r', encoding=encoding) as f:
                first_line = f.readline()
                separator = ';' if ';' in first_line else ','
            
            # Read CSV with detected separator and encoding
            df = pd.read_csv(filepath, sep=separator, encoding=encoding)
            break  # Success, exit loop
        except (UnicodeDecodeError, UnicodeError):
            continue  # Try next encoding
    
    if df is None:
        raise ValueError(f"Could not decode file with any of these encodings: {encodings}")
    
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


def transform_bookings_to_daily_occupancy(filepath, output_dir='data/processed'):
    """
    Transform booking-level data into daily occupancy dataset.
    
    Args:
        filepath (str): Path to raw bookings CSV file
        output_dir (str): Directory to save processed output (default: 'data/processed')
    
    Returns:
        pd.DataFrame: Daily occupancy dataframe with columns ['ds', 'y']
                      - ds: date
                      - y: occupancy (1 = occupied, 0 = free)
    
    Logic:
        - Read raw bookings CSV
        - Exclude cancellations (noches = 0)
        - Expand each booking into daily occupied nights
        - check_out is NOT counted as an occupied night
        - Create complete date range from min to max occupied date
        - Fill missing dates with y=0 (free nights)
        - Save to: {output_dir}/bookings_daily_occupancy_YYYYMMDD.csv
    """
    # Parse bookings
    df = parse_csv(filepath)
    
    occupied_nights = []
    cancellations = 0
    
    for _, row in df.iterrows():
        check_in = row['check_in']
        check_out = row['check_out']
        noches = row['noches']
        
        # Treat noches=0 as cancellations - exclude from analysis
        if noches <= 0:
            cancellations += 1
            continue
        
        # Generate occupied nights (check_out is NOT counted)
        current_date = check_in
        for _ in range(int(noches)):
            occupied_nights.append({'date': current_date})
            current_date += timedelta(days=1)
    
    if not occupied_nights:
        raise ValueError(f"No valid bookings to process. {cancellations} cancellations excluded.")
    
    # Create DataFrame with occupied nights
    occupied_df = pd.DataFrame(occupied_nights)
    
    # Mark all occupied nights with y=1
    occupied_df['y'] = 1
    
    # Remove duplicate dates (multiple bookings on same night)
    # Keep y=1 for any occupied night
    occupied_df = occupied_df.groupby('date')['y'].max().reset_index()
    
    # Create complete date range from min to max
    min_date = occupied_df['date'].min()
    max_date = occupied_df['date'].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Build complete dataframe with all dates
    complete_df = pd.DataFrame({'date': all_dates})
    
    # Merge with occupied nights (left join)
    daily_occupancy = complete_df.merge(occupied_df, on='date', how='left')
    
    # Fill missing values with 0 (free nights)
    daily_occupancy['y'] = daily_occupancy['y'].fillna(0).astype(int)
    
    # Rename columns to Prophet convention
    daily_occupancy.columns = ['ds', 'y']
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    output_filename = f'bookings_daily_occupancy_{timestamp}.csv'
    output_path = os.path.join(output_dir, output_filename)
    
    # Save to CSV
    daily_occupancy.to_csv(output_path, index=False)
    
    # Summary statistics
    total_days = len(daily_occupancy)
    occupied_days = (daily_occupancy['y'] == 1).sum()
    free_days = (daily_occupancy['y'] == 0).sum()
    occupancy_rate = (occupied_days / total_days) * 100
    
    print(f"✓ Created daily occupancy dataset: {output_filename}")
    print(f"  Date range: {min_date.date()} to {max_date.date()}")
    print(f"  Total days: {total_days}")
    print(f"  Occupied: {occupied_days} ({occupancy_rate:.1f}%)")
    print(f"  Free: {free_days} ({100-occupancy_rate:.1f}%)")
    print(f"  Excluded: {cancellations} cancellations")
    print(f"  Saved to: {output_path}")
    
    return daily_occupancy


def enrich_daily_occupancy_with_calendar(
    occupancy_filepath=None,
    occupancy_df=None,
    calendar_filepath='data/special_days_cl_2022_2040.csv',
    output_dir='data/processed'
):
    """
    Enrich daily occupancy dataset with Chilean calendar features.
    
    Args:
        occupancy_filepath (str): Path to daily occupancy CSV (optional if occupancy_df provided)
        occupancy_df (pd.DataFrame): Daily occupancy dataframe (optional if occupancy_filepath provided)
        calendar_filepath (str): Path to Chilean calendar CSV (default: special_days_cl_2022_2040.csv)
        output_dir (str): Directory to save enriched output (default: 'data/processed')
    
    Returns:
        pd.DataFrame: Enriched dataframe with columns:
            - ds: date
            - y: occupancy (1 = occupied, 0 = free)
            - day_of_week: 0=Monday, 6=Sunday
            - is_weekend: 1 if Saturday/Sunday, 0 otherwise
            - is_holiday: 1 if official holiday, 0 otherwise
            - is_sandwich: 1 if sandwich day, 0 otherwise
            - day_type: one of ['weekday', 'weekend', 'holiday', 'sandwich']
    
    Priority rules for day_type:
        1. If is_holiday=1 → 'holiday' (highest priority)
        2. Else if is_sandwich=1 → 'sandwich'
        3. Else if is_weekend=1 → 'weekend'
        4. Else → 'weekday'
    
    Logic:
        - Load daily occupancy dataset (ds, y)
        - Load Chilean calendar (holidays + sandwich days)
        - Derive weekend from ds (Saturday=5, Sunday=6)
        - Merge occupancy with calendar by date
        - Fill missing calendar values with 0
        - Determine day_type using priority rules
        - Save to: {output_dir}/features_daily_YYYYMMDD.csv
    """
    # Load occupancy data
    if occupancy_df is not None:
        df = occupancy_df.copy()
    elif occupancy_filepath is not None:
        df = pd.read_csv(occupancy_filepath)
        df['ds'] = pd.to_datetime(df['ds'])
    else:
        raise ValueError("Must provide either occupancy_filepath or occupancy_df")
    
    # Validate required columns
    if 'ds' not in df.columns or 'y' not in df.columns:
        raise ValueError("Occupancy dataset must have columns: ds, y")
    
    # Load Chilean calendar data
    try:
        # Try multiple encodings for calendar file
        calendar_df = None
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                calendar_df = pd.read_csv(calendar_filepath, encoding=encoding)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if calendar_df is None:
            raise ValueError(f"Could not decode calendar file with any encoding")
        
        # Parse date column
        calendar_df['date'] = pd.to_datetime(calendar_df['date'])
        
        # Select relevant columns
        required_cols = ['date', 'is_public_holiday', 'is_sandwich']
        if not all(col in calendar_df.columns for col in required_cols):
            raise ValueError(f"Calendar file missing required columns: {required_cols}")
        
        # Rename for clarity
        calendar_df = calendar_df[['date', 'is_public_holiday', 'is_sandwich']].copy()
        calendar_df.columns = ['ds', 'is_holiday', 'is_sandwich']
        
    except FileNotFoundError:
        print(f"⚠ Warning: Calendar file not found at {calendar_filepath}")
        print(f"  Proceeding without holiday/sandwich features (all set to 0)")
        calendar_df = pd.DataFrame({'ds': [], 'is_holiday': [], 'is_sandwich': []})
    
    # Add day of week (0=Monday, 6=Sunday)
    df['day_of_week'] = df['ds'].dt.dayofweek
    
    # Add weekend indicator (Saturday=5, Sunday=6)
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Merge with calendar data (left join to preserve all occupancy dates)
    enriched = df.merge(calendar_df, on='ds', how='left')
    
    # Fill missing calendar values with 0 (dates not in calendar = regular days)
    enriched['is_holiday'] = enriched['is_holiday'].fillna(0).astype(int)
    enriched['is_sandwich'] = enriched['is_sandwich'].fillna(0).astype(int)
    
    # Determine day_type using priority rules
    def assign_day_type(row):
        if row['is_holiday'] == 1:
            return 'holiday'
        elif row['is_sandwich'] == 1:
            return 'sandwich'
        elif row['is_weekend'] == 1:
            return 'weekend'
        else:
            return 'weekday'
    
    enriched['day_type'] = enriched.apply(assign_day_type, axis=1)
    
    # Reorder columns for clarity
    column_order = ['ds', 'y', 'day_of_week', 'is_weekend', 'is_holiday', 'is_sandwich', 'day_type']
    enriched = enriched[column_order]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    output_filename = f'features_daily_{timestamp}.csv'
    output_path = os.path.join(output_dir, output_filename)
    
    # Save to CSV
    enriched.to_csv(output_path, index=False)
    
    # Summary statistics
    total_days = len(enriched)
    weekdays = (enriched['day_type'] == 'weekday').sum()
    weekends = (enriched['day_type'] == 'weekend').sum()
    holidays = (enriched['day_type'] == 'holiday').sum()
    sandwiches = (enriched['day_type'] == 'sandwich').sum()
    
    print(f"✓ Created enriched features dataset: {output_filename}")
    print(f"  Total days: {total_days}")
    print(f"  Day type distribution:")
    print(f"    Weekdays: {weekdays} ({weekdays/total_days*100:.1f}%)")
    print(f"    Weekends: {weekends} ({weekends/total_days*100:.1f}%)")
    print(f"    Holidays: {holidays} ({holidays/total_days*100:.1f}%)")
    print(f"    Sandwich: {sandwiches} ({sandwiches/total_days*100:.1f}%)")
    print(f"  Saved to: {output_path}")
    
    return enriched
