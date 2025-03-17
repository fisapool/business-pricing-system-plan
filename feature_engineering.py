import pandas as pd
import numpy as np
from datetime import datetime

def engineer_features(df):
    # Time-based features
    df['day_of_week'] = pd.to_datetime(df['sale_date']).dt.dayofweek
    df['month'] = pd.to_datetime(df['sale_date']).dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Price-related features
    df['discount_percentage'] = (df['face_value'] - df['sale_price']) / df['face_value'] * 100
    df['price_difference_from_competitors'] = df['sale_price'] - df['competitor_avg_price']
    
    # Demand indicators
    df['days_since_last_purchase'] = df.groupby('gift_card_id')['sale_date'].diff().dt.days
    df['purchase_frequency'] = df.groupby('gift_card_id')['sale_date'].transform('count')
    
    # Seasonality and trend
    df['days_to_nearest_holiday'] = calculate_days_to_holiday(df['sale_date'])
    
    return df

def calculate_days_to_holiday(dates):
    """Calculate days to nearest major holiday"""
    # List of major US holidays (month, day)
    holidays = [
        (1, 1),    # New Year's Day
        (2, 14),   # Valentine's Day
        (7, 4),    # Independence Day
        (10, 31),  # Halloween
        (11, 25),  # Thanksgiving (approximation)
        (12, 25),  # Christmas
    ]
    
    dates = pd.to_datetime(dates)
    days_array = np.zeros(len(dates))
    
    for i, date in enumerate(dates):
        # Initialize with a large number
        min_days = 365
        
        for month, day in holidays:
            # Try current and next year
            current_year = date.year
            next_year = current_year + 1
            
            # Create holiday dates
            try:
                holiday_current = datetime(current_year, month, day)
                holiday_next = datetime(next_year, month, day)
                
                # Calculate days difference
                days_current = abs((date - pd.Timestamp(holiday_current)).days)
                days_next = abs((date - pd.Timestamp(holiday_next)).days)
                
                # Take minimum
                min_days = min(min_days, days_current, days_next)
            except ValueError:
                # Handle invalid dates (like Feb 29 in non-leap years)
                continue
        
        days_array[i] = min_days
    
    return days_array 