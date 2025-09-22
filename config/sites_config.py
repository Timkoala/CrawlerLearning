import os

def load_sites_config():
    """Load sites configuration from file"""
    sites_file = os.path.join(os.path.dirname(__file__), 'sites.txt')
    sites = []
    
    if os.path.exists(sites_file):
        with open(sites_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('|')
                    if len(parts) == 4:
                        sites.append({
                            'category': parts[0],
                            'country': parts[1],
                            'name': parts[2],
                            'url': parts[3]
                        })
    
    return sites

def get_sites_by_country(country):
    """Get sites filtered by country"""
    sites = load_sites_config()
    return [site for site in sites if site['country'] == country]

def get_sites_by_category(category):
    """Get sites filtered by category"""
    sites = load_sites_config()
    return [site for site in sites if site['category'] == category]

def get_countries():
    """Get list of unique countries"""
    sites = load_sites_config()
    countries = list(set(site['country'] for site in sites))
    return countries

def get_categories():
    """Get list of unique categories"""
    sites = load_sites_config()
    categories = list(set(site['category'] for site in sites))
    return categories