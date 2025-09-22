import sys
import os

# Add the project root to the Python path
sys.path.insert(0, r'D:\zfproj\qwScrapy')

# Set the Scrapy settings module
os.environ['SCRAPY_SETTINGS_MODULE'] = 'crawler.settings'

def test_crawler():
    try:
        print("Starting test crawler...")
        
        # Import after adding to path
        from crawler.spiders.custom_spider import CustomSpider
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        # Configure Scrapy settings
        settings = get_project_settings()
        settings.set('LOG_LEVEL', 'INFO')
        settings.set('USER_AGENT', 'test-crawler')
        
        # Create crawler process
        process = CrawlerProcess(settings)
        
        # Crawl with custom spider using the correct class name
        process.crawl(CustomSpider, 
                      job_id=999, 
                      target_url='http://quotes.toscrape.com', 
                      max_depth=1, 
                      custom_rules=None, 
                      name='custom_spider')  # 使用类名而不是随意的名字
        
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