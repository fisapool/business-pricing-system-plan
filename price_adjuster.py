import pandas as pd
import numpy as np
import joblib
import time
from datetime import datetime
import requests
import json

class PriceAdjuster:
    def __init__(self, model_path, config_path):
        self.model = joblib.load(model_path)
        self.config = self._load_config(config_path)
        self.price_history = {}
        self.competitor_cache = {}
        self.competitor_cache_time = {}
        
    def _load_config(self, path):
        """Load configuration including min/max price adjustments,
        competitor API endpoints, adjustment frequency, etc."""
        try:
            with open(path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            print(f"Config file not found: {path}")
            # Return default config
            return {
                'min_price_ratio': 0.7,
                'max_price_ratio': 1.2,
                'max_adjustment_percentage': 0.05,
                'competitor_cache_ttl': 3600,  # 1 hour
                'competitor_api_url': 'https://api.example.com/prices',
                'proxy_country': 'US',
                'default_competitor_prices': [48.50, 49.99, 47.95]
            }
    
    def get_competitor_prices(self, gift_card_id):
        # Check cache first to avoid excessive API calls
        current_time = time.time()
        if gift_card_id in self.competitor_cache and \
           current_time - self.competitor_cache_time[gift_card_id] < self.config['competitor_cache_ttl']:
            return self.competitor_cache[gift_card_id]
            
        # Otherwise fetch new data
        try:
            # Implementation for fetching competitor prices
            # using secure proxy connections via ProxyEthica
            from proxy_ethica import get_secure_proxy
            
            proxy = get_secure_proxy(country=self.config['proxy_country'])
            response = requests.get(
                self.config['competitor_api_url'],
                params={'gift_card_id': gift_card_id},
                proxies=proxy.get_dict(),
                timeout=5
            )
            prices = response.json()['prices']
            
            # Update cache
            self.competitor_cache[gift_card_id] = prices
            self.competitor_cache_time[gift_card_id] = current_time
            
            return prices
        except Exception as e:
            print(f"Error fetching competitor prices: {e}")
            # Fallback to cached values or defaults
            return self.competitor_cache.get(gift_card_id, self.config['default_competitor_prices'])
    
    def adjust_price(self, gift_card_data):
        # Get current market conditions
        competitor_prices = self.get_competitor_prices(gift_card_data['gift_card_id'])
        gift_card_data['competitor_avg_price'] = np.mean(competitor_prices)
        gift_card_data['competitor_min_price'] = min(competitor_prices)
        
        # Prepare features for the model
        features = self._prepare_features(gift_card_data)
        
        # Get optimal price from model
        optimal_price = self.model.predict(features)[0]
        
        # Apply business constraints
        optimal_price = max(optimal_price, gift_card_data['face_value'] * self.config['min_price_ratio'])
        optimal_price = min(optimal_price, gift_card_data['face_value'] * self.config['max_price_ratio'])
        
        # Gradual price adjustment to avoid dramatic changes
        current_price = gift_card_data['current_price']
        max_adjustment = current_price * self.config['max_adjustment_percentage']
        
        if abs(optimal_price - current_price) > max_adjustment:
            direction = 1 if optimal_price > current_price else -1
            new_price = current_price + (direction * max_adjustment)
        else:
            new_price = optimal_price
            
        # Round to appropriate price point (e.g., $19.99 instead of $20.00)
        new_price = self._apply_price_psychology(new_price)
        
        # Record adjustment for monitoring
        self._record_price_change(gift_card_data['gift_card_id'], current_price, new_price)
        
        return new_price
    
    def _prepare_features(self, gift_card_data):
        """Convert raw gift card data into features expected by the model"""
        import pandas as pd
        
        # Example implementation - adjust based on your model's requirements
        features = pd.DataFrame({
            'face_value': [gift_card_data['face_value']],
            'competitor_avg_price': [gift_card_data['competitor_avg_price']],
            'competitor_min_price': [gift_card_data['competitor_min_price']],
            'day_of_week': [pd.Timestamp.now().dayofweek],
            'month': [pd.Timestamp.now().month],
            'is_weekend': [1 if pd.Timestamp.now().dayofweek >= 5 else 0],
        })
        
        return features
        
    def _apply_price_psychology(self, price):
        # Apply psychological pricing (e.g., $19.99 instead of $20.00)
        if price >= 10:
            return np.floor(price) - 0.01
        else:
            return np.floor(price * 10) / 10 - 0.01
    
    def _record_price_change(self, gift_card_id, old_price, new_price):
        if gift_card_id not in self.price_history:
            self.price_history[gift_card_id] = []
            
        self.price_history[gift_card_id].append({
            'timestamp': datetime.now().isoformat(),
            'old_price': old_price,
            'new_price': new_price,
            'change_percentage': (new_price - old_price) / old_price * 100
        }) 