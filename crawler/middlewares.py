import random
import requests
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

class ProxyMiddleware:
    def __init__(self, proxy_list):
        self.proxy_list = proxy_list
        
    @classmethod
    def from_crawler(cls, crawler):
        proxy_list = crawler.settings.get('PROXY_LIST', [])
        return cls(proxy_list)
        
    def process_request(self, request, spider):
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = proxy
            
    def process_exception(self, request, exception, spider):
        # Rotate proxy on failure
        if self.proxy_list:
            proxy = random.choice(self.proxy_list)
            request.meta['proxy'] = proxy
            return request

class RandomUserAgentMiddleware:
    def __init__(self):
        self.user_agent_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        request.headers['User-Agent'] = ua

class AntiDetectionMiddleware:
    def __init__(self, download_delay):
        self.download_delay = download_delay
        
    @classmethod
    def from_crawler(cls, crawler):
        download_delay = crawler.settings.get('DOWNLOAD_DELAY', 3)
        return cls(download_delay)
        
    def process_request(self, request, spider):
        # Add random delay
        delay = random.uniform(0.5 * self.download_delay, 1.5 * self.download_delay)
        request.meta['download_delay'] = delay