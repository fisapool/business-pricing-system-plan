import pandas as pd
import joblib
import argparse
import logging
from pathlib import Path
import json
import time
from datetime import datetime, timedelta
import os

from pricing_model.feature_engineering import engineer_features
from pricing_model.model_selection import select_best_model
from pricing_model.price_adjuster import PriceAdjuster
from pricing_model.ab_testing import ABTest
from pricing_model.market_data import MarketDataCollector
from pricing_model.seasonality import train_seasonality_model, predict_seasonal_effect
from pricing_model.dashboard_generator import DashboardGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pricing_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GiftCardPricing")

def train_models(data_path, output_dir):
    logger.info(f"Loading data from {data_path}")
    df = pd.read_csv(data_path)
    
    # Feature engineering
    df = engineer_features(df)
    
    # Group by gift card type
    gift_card_types = df['gift_card_type'].unique()
    models = {}
    
    for gc_type in gift_card_types:
        logger.info(f"Training model for {gc_type}")
        gc_data = df[df['gift_card_type'] == gc_type]
        
        # Prepare features and target
        X = gc_data.drop(['gift_card_id', 'sale_date', 'sale_price', 'gift_card_type'], axis=1)
        y = gc_data['sale_price']
        
        # Train-validation split
        from sklearn.model_selection import train_test_split
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Select and train the best model
        best_model = select_best_model(X_train, y_train, X_val, y_val)
        
        # Train seasonality model
        seasonality_data = gc_data[['sale_date', 'sale_price']]
        seasonality_model = train_seasonality_model(seasonality_data)
        
        # Save models
        output_path = Path(output_dir) / f"{gc_type.lower().replace(' ', '_')}_model.pkl"
        seasonality_path = Path(output_dir) / f"{gc_type.lower().replace(' ', '_')}_seasonality.pkl"
        
        joblib.dump(best_model, output_path)
        joblib.dump(seasonality_model, seasonality_path)
        
        models[gc_type] = {
            'model_path': str(output_path),
            'seasonality_path': str(seasonality_path),
            'features': list(X.columns)
        }
    
    # Save model metadata
    with open(Path(output_dir) / "model_metadata.json", 'w') as f:
        json.dump(models, f, indent=2)
    
    logger.info(f"Models trained and saved to {output_dir}")
    return models

def update_dashboard(data_dir, dashboard_dir=None):
    """Update the dashboard with latest data"""
    if dashboard_dir is None:
        dashboard_dir = Path(data_dir).parent / "dashboard"
    
    logger.info(f"Updating dashboard at {dashboard_dir}")
    generator = DashboardGenerator(data_dir, dashboard_dir)
    generator.generate_dashboard()
    
    # Record price history for dashboard
    price_history_file = Path(data_dir) / "price_update_history.csv"
    
    return dashboard_dir

def run_price_optimization(config_path, data_dir):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Load model metadata
    with open(Path(data_dir) / "model_metadata.json", 'r') as f:
        model_metadata = json.load(f)
    
    # Initialize market data collector
    market_collector = MarketDataCollector(config_path)
    
    # Initialize price adjusters for each gift card type
    adjusters = {}
    for gc_type, metadata in model_metadata.items():
        adjusters[gc_type] = PriceAdjuster(metadata['model_path'], config_path)
    
    # Initialize A/B testing
    ab_test = ABTest("price_optimization_v1", experiment_duration_days=14)
    
    # Load current inventory
    inventory_df = pd.read_csv(Path(data_dir) / "current_inventory.csv")
    
    # Initialize dashboard update timer
    last_dashboard_update = datetime.now()
    dashboard_update_interval = timedelta(hours=config.get('dashboard_update_interval_hours', 6))
    
    while True:
        try:
            # Collect latest market data
            gift_card_brands = inventory_df['brand'].unique().tolist()
            market_data = market_collector.collect_competitor_prices(gift_card_brands)
            
            # Update prices for each item in inventory
            updated_prices = []
            
            for _, item in inventory_df.iterrows():
                gc_type = item['gift_card_type']
                
                if gc_type in adjusters:
                    # Prepare item data with market information
                    item_data = item.to_dict()
                    item_data['competitor_prices'] = market_data.get(item['brand'], [])
                    
                    # Get optimal price
                    optimal_price = adjusters[gc_type].adjust_price(item_data)
                    
                    # Apply A/B testing
                    final_price = ab_test.get_price(
                        item['gift_card_id'], 
                        optimal_price,
                        item['current_price']
                    )
                    
                    updated_prices.append({
                        'gift_card_id': item['gift_card_id'],
                        'old_price': item['current_price'],
                        'new_price': final_price,
                        'change': final_price - item['current_price'],
                        'change_percentage': ((final_price - item['current_price']) / item['current_price']) * 100
                    })
            
            # Log price changes
            changes_df = pd.DataFrame(updated_prices)
            logger.info(f"Price updates generated: {len(changes_df)} items")
            logger.info(f"Average change: {changes_df['change_percentage'].mean():.2f}%")
            
            # Save updates to file for API to pick up
            changes_df.to_csv(Path(data_dir) / "price_updates.csv", index=False)
            
            # Update price history for dashboard
            price_history_file = Path(data_dir) / "price_update_history.csv"
            if price_history_file.exists():
                history_df = pd.read_csv(price_history_file)
                # Add timestamp column if it doesn't exist
                if 'timestamp' not in history_df.columns:
                    history_df['timestamp'] = pd.Timestamp.now().isoformat()
                # Append new changes
                history_df = pd.concat([history_df, changes_df.assign(timestamp=pd.Timestamp.now().isoformat())], ignore_index=True)
            else:
                history_df = changes_df.assign(timestamp=pd.Timestamp.now().isoformat())
            
            # Save updated history
            history_df.to_csv(price_history_file, index=False)
            
            # Update dashboard if interval has passed
            current_time = datetime.now()
            if current_time - last_dashboard_update > dashboard_update_interval:
                update_dashboard(data_dir)
                last_dashboard_update = current_time
            
            # Sleep until next cycle
            logger.info(f"Sleeping for {config['update_interval_minutes']} minutes")
            time.sleep(config['update_interval_minutes'] * 60)
            
        except KeyboardInterrupt:
            logger.info("Optimization process interrupted by user")
            break
        except Exception as e:
            logger.error(f"Error in optimization cycle: {str(e)}")
            time.sleep(60)  # Sleep and retry
    
    # Clean up
    market_collector.close()
    logger.info("Price optimization process completed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gift Card Price Optimization System")
    parser.add_argument('--train', action='store_true', help='Train new models')
    parser.add_argument('--optimize', action='store_true', help='Run price optimization')
    parser.add_argument('--data-path', type=str, default='data/historical_sales.csv', help='Path to training data')
    parser.add_argument('--output-dir', type=str, default='models', help='Directory to save models')
    parser.add_argument('--config', type=str, default='config/pricing_config.json', help='Configuration file path')
    parser.add_argument('--data-dir', type=str, default='data', help='Data directory for current inventory and updates')
    parser.add_argument('--update-dashboard', action='store_true', help='Update the dashboard')
    parser.add_argument('--dashboard-dir', type=str, default=None, help='Dashboard output directory')
    
    args = parser.parse_args()
    
    if args.train:
        train_models(args.data_path, args.output_dir)
    
    if args.optimize:
        run_price_optimization(args.config, args.data_dir)
    
    if args.update_dashboard:
        update_dashboard(args.data_dir, args.dashboard_dir) 