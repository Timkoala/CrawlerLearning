import json
import os

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            # Return default configuration
            return {
                "general": {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "concurrent_requests": 16,
                    "download_delay": 3
                },
                "proxy": {
                    "enabled": False,
                    "list": []
                },
                "anti_detection": {
                    "random_user_agent": True,
                    "rotate_proxy": True,
                    "respect_robots": True
                }
            }
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def get(self, section, key, default=None):
        """Get a configuration value"""
        return self.config.get(section, {}).get(key, default)
        
    def set(self, section, key, value):
        """Set a configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
        
    def get_all(self):
        """Get all configuration"""
        return self.config
        
    def update(self, new_config):
        """Update configuration with new values"""
        self.config.update(new_config)
        self.save_config()