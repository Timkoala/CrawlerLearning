import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_crawler():
    try:
        # Import after adding to path
        from crawler.spiders.custom_spider import CustomSpider
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        print("Starting test crawler...")
        
        # Configure Scrapy settings
        settings = get_project_settings()
        settings.set('LOG_LEVEL', 'INFO')
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Crawl with custom spider
        process.crawl(CustomSpider, 
                      job_id=999, 
                      target_url='http://quotes.toscrape.com', 
                      max_depth=1, 
                      custom_rules=None, 
                      name='test_spider')
        
        print("Starting crawl process...")
        # Start the crawling process
        process.start()
        print("Crawl process completed.")
        
    except Exception as e:
        print(f"Error running test crawler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_crawler()