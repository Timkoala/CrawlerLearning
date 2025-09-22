import scrapy
from scrapy.http import Request

class BaseSpider(scrapy.Spider):
    name = 'base_spider'
    
    def __init__(self, start_urls=None, max_depth=1, *args, **kwargs):
        super(BaseSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls or []
        self.max_depth = int(max_depth)
        
    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, meta={'depth': 1})
            
    def parse(self, response):
        # Extract data from the page
        item = {
            'url': response.url,
            'title': response.css('title::text').get(),
            'content': ' '.join(response.css('body ::text').getall()).strip(),
            'links': response.css('a::attr(href)').getall()
        }
        
        yield item
        
        # Follow links if depth allows
        current_depth = response.meta.get('depth', 1)
        if current_depth < self.max_depth:
            for link in response.css('a::attr(href)').getall():
                # Convert relative URLs to absolute
                absolute_url = response.urljoin(link)
                yield Request(absolute_url, callback=self.parse, meta={'depth': current_depth + 1})