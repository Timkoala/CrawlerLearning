import random
import time

def get_random_proxy(proxy_list):
    """Get a random proxy from the proxy list"""
    if proxy_list:
        return random.choice(proxy_list)
    return None

def rotate_user_agent(user_agent_list):
    """Get a random user agent from the list"""
    if user_agent_list:
        return random.choice(user_agent_list)
    return None

def random_delay(min_delay=1, max_delay=5):
    """Generate a random delay"""
    return random.uniform(min_delay, max_delay)