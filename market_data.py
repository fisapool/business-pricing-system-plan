from proxy_ethica import ProxySession, RobotsParser
import requests
import pandas as pd
import json

class MarketDataCollector:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        self.proxy_session = None
        
    def initialize_proxy(self):
        # Create a new proxy session with proper fallback strategies
        self.proxy_session = ProxySession(
            country=self.config['proxy_country'],
            city=self.config['proxy_city'],
            enable_rotation=True,
            rotation_interval=300,  # Rotate IP every 5 minutes
            fallback_countries=['US', 'UK', 'CA'],  # Fallback countries if primary fails
            protocol_fallbacks=['https', 'http', 'socks5'],
            respect_robots_txt=True,
            track_bandwidth=True
        )
        
    def collect_competitor_prices(self, gift_card_brands):
        if not self.proxy_session:
            self.initialize_proxy()
            
        results = {}
        
        for brand in gift_card_brands:
            sources = self.config['data_sources'].get(brand, self.config['data_sources']['default'])
            brand_prices = []
            
            for source in sources:
                try:
                    # Check if scraping is allowed by robots.txt
                    robots_parser = RobotsParser(source['base_url'])
                    if not robots_parser.can_fetch(source['endpoint']):
                        print(f"Scraping not allowed for {source['base_url']}")
                        continue
                    
                    # Random delay to avoid detection
                    self.proxy_session.random_delay(min_seconds=1, max_seconds=3)
                    
                    # Make the request with a clean user agent
                    response = self.proxy_session.get(
                        f"{source['base_url']}{source['endpoint']}",
                        params={'brand': brand, 'format': 'json'},
                        headers={'User-Agent': self.proxy_session.get_random_user_agent()}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'prices' in data:
                            brand_prices.extend(data['prices'])
                    else:
                        print(f"Failed to fetch data from {source['base_url']}: {response.status_code}")
                        
                except Exception as e:
                    print(f"Error collecting data from {source['base_url']}: {str(e)}")
                    # Try fallback if available
                    if 'fallback_endpoint' in source:
                        try:
                            response = self.proxy_session.get(
                                f"{source['base_url']}{source['fallback_endpoint']}",
                                params={'brand': brand}
                            )
                            if response.status_code == 200:
                                data = response.json()
                                brand_prices.extend(data.get('prices', []))
                        except Exception as fallback_error:
                            print(f"Fallback also failed: {str(fallback_error)}")
            
            results[brand] = brand_prices
            
        return results
        
    def close(self):
        if self.proxy_session:
            self.proxy_session.close() 