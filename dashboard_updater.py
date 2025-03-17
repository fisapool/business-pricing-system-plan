import os
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime, timedelta
import random
import logging
from pricing_model.dashboard_generator import DashboardGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DashboardUpdater")

def create_sample_data(data_dir):
    """Create sample data files for testing the dashboard if real data doesn't exist"""
    data_dir = Path(data_dir)
    data_dir.mkdir(exist_ok=True)
    
    # Generate sample price update history
    if not (data_dir / "price_update_history.csv").exists():
        logger.info("Generating sample price update history")
        # Create 90 days of data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        dates = [start_date + timedelta(days=i) for i in range(91)]
        
        # Gift card types
        card_types = ["Netflix", "Amazon", "Steam", "iTunes", "Uber", "Starbucks"]
        
        # Generate records
        records = []
        for date in dates:
            for card_type in card_types:
                # Generate between 5-20 price changes per day per card type
                num_changes = random.randint(5, 20)
                for _ in range(num_changes):
                    change_pct = random.uniform(-5, 5)
                    old_price = random.uniform(40, 95)
                    new_price = old_price * (1 + change_pct/100)
                    
                    records.append({
                        "timestamp": date.isoformat(),
                        "gift_card_id": f"{card_type}-{random.randint(1000, 9999)}",
                        "gift_card_type": card_type,
                        "old_price": old_price,
                        "new_price": new_price,
                        "change_percentage": change_pct
                    })
        
        # Create dataframe and save to CSV
        df = pd.DataFrame(records)
        df.to_csv(data_dir / "price_update_history.csv", index=False)
    
    # Generate sample A/B test results
    if not (data_dir / "ab_test_results.csv").exists():
        logger.info("Generating sample A/B test results")
        # Create 12 weeks of A/B test results
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=12)
        dates = [start_date + timedelta(weeks=i) for i in range(13)]
        
        records = []
        for i, date in enumerate(dates):
            # Simulate improving results over time
            improvement_factor = i / 12  # 0 to 1
            
            control_conversion = 0.12 + random.uniform(-0.01, 0.01)
            test_conversion = control_conversion * (1 + 0.15 * improvement_factor + random.uniform(-0.02, 0.05))
            
            control_revenue = 45 + random.uniform(-2, 2)
            test_revenue = control_revenue * (1 + 0.1 * improvement_factor + random.uniform(-0.01, 0.03))
            
            control_profit = 4.5 + random.uniform(-0.5, 0.5)
            test_profit = control_profit * (1 + 0.2 * improvement_factor + random.uniform(-0.02, 0.04))
            
            p_value = max(0.001, 0.1 - (0.095 * improvement_factor))
            
            records.append({
                "date": date.strftime("%Y-%m-%d"),
                "control_count": random.randint(800, 1200),
                "test_count": random.randint(800, 1200),
                "control_conversion_rate": control_conversion,
                "test_conversion_rate": test_conversion,
                "control_revenue_per_user": control_revenue,
                "test_revenue_per_user": test_revenue,
                "control_profit_per_user": control_profit,
                "test_profit_per_user": test_profit,
                "revenue_lift": ((test_revenue / control_revenue) - 1) * 100,
                "profit_lift": ((test_profit / control_profit) - 1) * 100,
                "p_value": p_value,
                "lift_percentage": ((test_profit / control_profit) - 1) * 100
            })
        
        # Create dataframe and save to CSV
        df = pd.DataFrame(records)
        df.to_csv(data_dir / "ab_test_results.csv", index=False)
    
    # Generate sample model performance data
    if not (data_dir / "model_performance.csv").exists():
        logger.info("Generating sample model performance data")
        models = [
            "random_forest_netflix", 
            "xgboost_netflix",
            "lightgbm_netflix",
            "random_forest_amazon",
            "xgboost_amazon",
            "lightgbm_amazon"
        ]
        
        records = []
        for model in models:
            base_mae = 0.8 + random.uniform(-0.2, 0.2)
            base_rmse = base_mae * 1.2 + random.uniform(-0.1, 0.1)
            
            # Create feature importance (simulated)
            feature_importance = {
                "competitor_price": random.uniform(0.2, 0.4),
                "day_of_week": random.uniform(0.05, 0.15),
                "is_weekend": random.uniform(0.05, 0.1),
                "month": random.uniform(0.1, 0.2),
                "discount_percentage": random.uniform(0.15, 0.3),
                "days_to_holiday": random.uniform(0.05, 0.15)
            }
            
            # Normalize to sum to 1
            importance_sum = sum(feature_importance.values())
            feature_importance = {k: v/importance_sum for k, v in feature_importance.items()}
            
            records.append({
                "model_name": model,
                "mae": base_mae,
                "rmse": base_rmse,
                "r_squared": random.uniform(0.75, 0.92),
                "training_time": random.uniform(5, 30),
                "feature_importance": json.dumps(feature_importance)
            })
        
        # Create dataframe and save to CSV
        df = pd.DataFrame(records)
        df.to_csv(data_dir / "model_performance.csv", index=False)
    
    # Generate sample inventory data
    if not (data_dir / "current_inventory.csv").exists():
        logger.info("Generating sample inventory data")
        card_types = ["Netflix", "Amazon", "Steam", "iTunes", "Uber", "Starbucks"]
        face_values = [25, 50, 100]
        
        records = []
        for card_type in card_types:
            for face_value in face_values:
                # Generate between 10-30 cards of each type and value
                num_cards = random.randint(10, 30)
                for i in range(num_cards):
                    discount = random.uniform(3, 12)
                    current_price = face_value * (1 - discount/100)
                    profit_margin = discount - random.uniform(0.5, 2)  # Account for costs
                    
                    records.append({
                        "gift_card_id": f"{card_type}-{face_value}-{i}",
                        "gift_card_type": card_type,
                        "face_value": face_value,
                        "current_price": current_price,
                        "profit_margin": profit_margin,
                        "brand": card_type
                    })
        
        # Create dataframe and save to CSV
        df = pd.DataFrame(records)
        df.to_csv(data_dir / "current_inventory.csv", index=False)
    
    logger.info("Sample data creation complete")

def main():
    """Main function to update the dashboard"""
    # Define directories
    data_dir = Path("data")
    dashboard_dir = Path("dashboard")
    
    # Create sample data for testing (will only create if files don't exist)
    create_sample_data(data_dir)
    
    # Generate dashboard
    logger.info("Generating dashboard")
    generator = DashboardGenerator(data_dir, dashboard_dir)
    generator.generate_dashboard()
    
    # Create a .nojekyll file to disable Jekyll processing
    with open(dashboard_dir / ".nojekyll", "w") as f:
        pass
    
    logger.info(f"Dashboard successfully generated at {dashboard_dir}")
    
    # If running in GitHub Actions, create a timestamp file
    if os.environ.get('GITHUB_ACTIONS'):
        with open(dashboard_dir / "last_update.txt", "w") as f:
            f.write(f"Dashboard last updated: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main() 