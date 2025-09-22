import scrapy
from scrapy.http import Request
import json
import logging

class CustomSpider(scrapy.Spider):
    """Custom spider class that can be pickled and supports custom rules"""
    
    def __init__(self, job_id=None, run_id=None, target_url=None, max_depth=1, custom_rules=None, *args, **kwargs):
        super(CustomSpider, self).__init__(*args, **kwargs)
        self.job_id = job_id if job_id is not None else getattr(self, 'job_id', 'unknown')
        self.run_id = run_id
        if target_url:
            self.start_urls = [target_url]
        self.max_depth = int(max_depth)
        self.custom_rules = custom_rules or {}
        self.log(f"[Job {self.job_id}] Initializing CustomSpider (run_id={self.run_id})", level=logging.INFO)
    
    async def start(self):
        # Scrapy 2.13+ coroutine start
        self.log(f"[Job {self.job_id}] Starting crawl with URLs: {getattr(self, 'start_urls', [])}", level=logging.INFO)
        for url in getattr(self, 'start_urls', []):
            yield Request(url, callback=self.parse, errback=self.handle_error, meta={'depth': 1})
    
    def start_requests(self):
        # Backward compatibility for <2.13
        for url in getattr(self, 'start_urls', []):
            yield Request(url, callback=self.parse, errback=self.handle_error, meta={'depth': 1})
            
    def parse(self, response):
        self.log(f"[Job {self.job_id}] Received response from: {response.url} (status: {response.status})", level=logging.INFO)
        item = self.extract_data(response)
        item['url'] = response.url
        item['job_id'] = self.job_id
        item['run_id'] = self.run_id
        yield item
        current_depth = response.meta.get('depth', 1)
        if current_depth < self.max_depth:
            links = response.css('a::attr(href)').getall()
            for link in links:
                absolute_url = response.urljoin(link)
                if not absolute_url or absolute_url.startswith('javascript:'):
                    continue
                yield Request(absolute_url, callback=self.parse, errback=self.handle_error, meta={'depth': current_depth + 1})
    
    def handle_error(self, failure):
        request = failure.request
        response = getattr(failure.value, 'response', None)
        status = response.status if response else None
        self.log(f"[Job {self.job_id}] Request failed {request.url} status={status}", level=logging.INFO)
        # Save placeholder item for visibility on 4xx/5xx
        try:
            yield {
                'url': request.url,
                'job_id': self.job_id,
                'run_id': self.run_id,
                'title': None,
                'content': None,
                'error_status': status,
                'links': []
            }
        except Exception:
            pass
    
    def extract_data(self, response):
        self.log(f"[Job {self.job_id}] Starting data extraction from: {response.url}", level=logging.INFO)
        if self.custom_rules:
            return self.extract_with_rules(response)
        else:
            title = response.css('title::text').get()
            content = ' '.join(response.css('body ::text').getall()).strip()[:500]
            links = response.css('a::attr(href)').getall()
            return { 'title': title, 'content': content, 'links': links }
    
    def extract_with_rules(self, response):
        extracted_data = {}
        if 'title_selector' in self.custom_rules:
            extracted_data['title'] = response.css(self.custom_rules['title_selector']).get()
        else:
            extracted_data['title'] = response.css('title::text').get()
        if 'content_selector' in self.custom_rules:
            texts = response.css(self.custom_rules['content_selector']).getall()
            extracted_data['content'] = ' '.join(texts).strip()[:1000]
        else:
            extracted_data['content'] = ' '.join(response.css('body ::text').getall()).strip()[:500]
        if 'custom_fields' in self.custom_rules:
            for field_name, selector in self.custom_rules['custom_fields'].items():
                values = response.css(selector).getall()
                extracted_data[field_name] = values[0] if len(values) == 1 else values
        return extracted_data