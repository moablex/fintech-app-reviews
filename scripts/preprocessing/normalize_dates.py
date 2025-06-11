# preprocessing/normalize_dates.py
import pandas as pd

def normalize_dates(df: pd.DataFrame, date_column: str = "date") -> pd.DataFrame:
    # Convert to datetime
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    
    # Identify invalid dates
    invalid_mask = df[date_column].isna()
    invalid_count = invalid_mask.sum()
    
    if invalid_count > 0:
        print(f"Found {invalid_count} rows with invalid dates")
        
        # Calculate median date from valid dates
        valid_dates = df[~invalid_mask][date_column]
        median_date = valid_dates.median()
        
        # Fill missing/invalid dates with the median
        df.loc[invalid_mask, date_column] = median_date
    
    # Convert to YYYY-MM-DD format
    df[date_column] = df[date_column].dt.strftime('%Y-%m-%d')
    
    return df