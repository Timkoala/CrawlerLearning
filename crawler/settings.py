# Scrapy settings for crawler project

BOT_NAME = 'crawler'

SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Concurrency
CONCURRENT_REQUESTS = 16

# Download delay
DOWNLOAD_DELAY = 0.5

# Allow HTTP error codes like 403 so spider can handle/log them
HTTPERROR_ALLOWED_CODES = [403, 404]
RETRY_ENABLED = True
RETRY_TIMES = 2

# Default request headers / UA via middleware

# Enable downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'crawler.middlewares.RandomUserAgentMiddleware': 400,
}

# Item pipelines
ITEM_PIPELINES = {
    'crawler.pipelines.JsonWriterPipeline': 300,
    'crawler.pipelines.DatabasePipeline': 400,
}

# Twisted & logging
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'
LOG_LEVEL = 'INFO'
LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'