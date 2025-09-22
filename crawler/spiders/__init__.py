# This file is automatically created by Scrapy when starting a project
# It's used to register spiders in the project

import scrapy
from crawler.spiders.custom_spider import CustomSpider

# Register the CustomSpider class
class CustomSpiderWrapper(CustomSpider):
    name = 'custom_spider'  # This is the name that will be used in the command line