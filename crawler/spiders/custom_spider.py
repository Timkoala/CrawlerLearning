import scrapy
from scrapy.http import Request
import json
import logging

class CustomSpider(scrapy.Spider):
    """Custom spider class that can be pickled and supports custom rules"""
    
    def __init__(self, job_id=None, target_url=None, max_depth=1, custom_rules=None, *args, **kwargs):
        # 不要在这里设置name属性，而是通过kwargs传递
        super(CustomSpider, self).__init__(*args, **kwargs)
        
        # 如果job_id存在，设置spider的name
        if job_id is not None:
            self.job_id = job_id
            # name属性需要在Spider初始化时通过kwargs设置，不能在初始化后设置
        else:
            self.job_id = getattr(self, 'job_id', 'unknown')
            
        # 设置其他属性
        if target_url:
            self.start_urls = [target_url]
        self.max_depth = int(max_depth)
        # Custom rules for data extraction
        self.custom_rules = custom_rules or {}
        
        # 不要设置self.logger，使用Scrapy内置的logger
        # 记录初始化信息
        self.log(f"[Job {self.job_id}] Initializing CustomSpider", level=logging.INFO)
        
    def start_requests(self):
        self.log(f"[Job {self.job_id}] Starting crawl with URLs: {getattr(self, 'start_urls', [])}", level=logging.INFO)
        for url in getattr(self, 'start_urls', []):
            self.log(f"[Job {self.job_id}] Sending request to: {url}", level=logging.INFO)
            yield Request(url, callback=self.parse, meta={'depth': 1})
            
    def parse(self, response):
        self.log(f"[Job {self.job_id}] Received response from: {response.url} (status: {response.status})", level=logging.INFO)
        
        # Log response details
        self.log(f"[Job {self.job_id}] Response headers: {dict(response.headers)}", level=logging.INFO)
        self.log(f"[Job {self.job_id}] Response body length: {len(response.body)}", level=logging.INFO)
        
        # Extract data based on custom rules or default rules
        item = self.extract_data(response)
        item['url'] = response.url
        item['job_id'] = self.job_id
        
        self.log(f"[Job {self.job_id}] Extracted item: {item}", level=logging.INFO)
        yield item
        
        # Follow links if depth allows
        current_depth = response.meta.get('depth', 1)
        self.log(f"[Job {self.job_id}] Current depth: {current_depth}, Max depth: {self.max_depth}", level=logging.INFO)
        
        if current_depth < self.max_depth:
            links = response.css('a::attr(href)').getall()
            self.log(f"[Job {self.job_id}] Found {len(links)} links to follow", level=logging.INFO)
            
            for i, link in enumerate(links[:10]):  # Limit to first 10 links for logging
                # Convert relative URLs to absolute
                absolute_url = response.urljoin(link)
                self.log(f"[Job {self.job_id}] Following link {i+1}: {absolute_url}", level=logging.INFO)
                yield Request(absolute_url, callback=self.parse, meta={'depth': current_depth + 1})
                
            if len(links) > 10:
                self.log(f"[Job {self.job_id}] Skipping {len(links) - 10} additional links (logging limited to 10)", level=logging.INFO)
        else:
            self.log(f"[Job {self.job_id}] Reached max depth, not following more links", level=logging.INFO)
    
    def extract_data(self, response):
        """Extract data based on custom rules or use default extraction"""
        self.log(f"[Job {self.job_id}] Starting data extraction from: {response.url}", level=logging.INFO)
        
        # Log first 500 characters of response body for context
        self.log(f"[Job {self.job_id}] Page content preview: {response.text[:500]}...", level=logging.INFO)
        
        # If custom rules are provided, use them
        if self.custom_rules:
            return self.extract_with_rules(response)
        else:
            # Default extraction
            title = response.css('title::text').get()
            content = ' '.join(response.css('body ::text').getall()).strip()[:500]
            links = response.css('a::attr(href)').getall()[:10]
            
            self.log(f"[Job {self.job_id}] Default extraction - Title: {title}", level=logging.INFO)
            self.log(f"[Job {self.job_id}] Default extraction - Content length: {len(content)}", level=logging.INFO)
            self.log(f"[Job {self.job_id}] Default extraction - Links count: {len(links)}", level=logging.INFO)
            
            return {
                'title': title,
                'content': content,
                'links': links
            }
    
    def extract_with_rules(self, response):
        """Extract data based on custom rules"""
        self.log(f"[Job {self.job_id}] Starting extraction with custom rules", level=logging.INFO)
        extracted_data = {}
        
        # Extract title
        if 'title_selector' in self.custom_rules:
            title = response.css(self.custom_rules['title_selector']).get()
            extracted_data['title'] = title
            self.log(f"[Job {self.job_id}] Custom title extraction: {title}", level=logging.INFO)
        else:
            title = response.css('title::text').get()
            extracted_data['title'] = title
            self.log(f"[Job {self.job_id}] Default title extraction: {title}", level=logging.INFO)
        
        # Extract content
        if 'content_selector' in self.custom_rules:
            content_texts = response.css(self.custom_rules['content_selector']).getall()
            content = ' '.join(content_texts).strip()[:1000]
            extracted_data['content'] = content
            self.log(f"[Job {self.job_id}] Custom content extraction - Length: {len(content)}", level=logging.INFO)
        else:
            content = ' '.join(response.css('body ::text').getall()).strip()[:500]
            extracted_data['content'] = content
            self.log(f"[Job {self.job_id}] Default content extraction - Length: {len(content)}", level=logging.INFO)
        
        # Extract custom fields
        if 'custom_fields' in self.custom_rules:
            self.log(f"[Job {self.job_id}] Extracting {len(self.custom_rules['custom_fields'])} custom fields", level=logging.INFO)
            for field_name, selector in self.custom_rules['custom_fields'].items():
                values = response.css(selector).getall()
                if len(values) == 1:
                    extracted_data[field_name] = values[0]
                    self.log(f"[Job {self.job_id}] Custom field '{field_name}': {values[0]}", level=logging.INFO)
                else:
                    extracted_data[field_name] = values
                    self.log(f"[Job {self.job_id}] Custom field '{field_name}' (multiple values): {len(values)} items", level=logging.INFO)
        
        return extracted_data