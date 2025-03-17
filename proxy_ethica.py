"""
Mock implementation of the proxy_ethica package for development
"""

class ProxySession:
    def __init__(self, country=None, city=None, enable_rotation=False, 
                 rotation_interval=300, fallback_countries=None, 
                 protocol_fallbacks=None, respect_robots_txt=True, 
                 track_bandwidth=False):
        self.country = country
        self.city = city
        self.enable_rotation = enable_rotation
        self.rotation_interval = rotation_interval
        self.fallback_countries = fallback_countries or []
        self.protocol_fallbacks = protocol_fallbacks or []
        self.respect_robots_txt = respect_robots_txt
        self.track_bandwidth = track_bandwidth
        print(f"Mock ProxySession initialized for {country}")
    
    def get(self, url, params=None, headers=None, proxies=None, timeout=None):
        """Mock HTTP GET request"""
        import requests
        from requests.models import Response
        
        print(f"Mock request to: {url}")
        
        # Return a mock response
        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"prices": [49.99, 48.50, 47.99]}'
        mock_response.url = url
        mock_response.headers = {'Content-Type': 'application/json'}
        return mock_response
    
    def random_delay(self, min_seconds=1, max_seconds=3):
        """Mock delay function"""
        import time
        import random
        delay = random.uniform(min_seconds, max_seconds)
        print(f"Mock delay: {delay:.2f} seconds")
        time.sleep(0.1)  # Just a minimal delay for testing
    
    def get_random_user_agent(self):
        """Return a random user agent string"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        import random
        return random.choice(user_agents)
    
    def close(self):
        """Close the session"""
        print("Mock session closed")

class RobotsParser:
    def __init__(self, url):
        self.url = url
        print(f"Mock RobotsParser initialized for {url}")
    
    def can_fetch(self, endpoint):
        """Always return True for mock implementation"""
        return True

def get_secure_proxy(country=None):
    """Get a secure proxy for the specified country"""
    return ProxySession(country=country) 