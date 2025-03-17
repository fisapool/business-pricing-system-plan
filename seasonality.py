from prophet import Prophet
import pandas as pd

def train_seasonality_model(historical_data):
    # Prepare data in Prophet format
    df = pd.DataFrame({
        'ds': pd.to_datetime(historical_data['sale_date']),
        'y': historical_data['sale_price']
    })
    
    # Initialize and train model
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        seasonality_mode='multiplicative'
    )
    
    # Add holiday effects
    model.add_country_holidays(country_name='US')
    
    # Fit model
    model.fit(df)
    
    return model

def predict_seasonal_effect(model, future_dates):
    # Create future dataframe
    future = pd.DataFrame({'ds': pd.to_datetime(future_dates)})
    
    # Make prediction
    forecast = model.predict(future)
    
    # Extract seasonal components
    seasonal_effects = forecast[['ds', 'trend', 'yearly', 'weekly', 'holidays']]
    
    return seasonal_effects 