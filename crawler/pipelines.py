import json
from itemadapter import ItemAdapter
import logging

class JsonWriterPipeline:
    def open_spider(self, spider):
        self.file = open('items.json', 'w')
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"[Pipeline] Opening JSON writer for spider: {spider.name}")

    def close_spider(self, spider):
        self.file.close()
        self.logger.info(f"[Pipeline] Closing JSON writer for spider: {spider.name}")

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        self.logger.info(f"[Pipeline] Written item to JSON: {item}")
        return item

class DatabasePipeline:
    def __init__(self):
        # Initialize database connection
        self.logger = logging.getLogger(__name__)
        pass
        
    def open_spider(self, spider):
        # Setup database connection
        self.logger.info(f"[Pipeline] Opening database connection for spider: {spider.name}")
        pass

    def close_spider(self, spider):
        # Close database connection
        self.logger.info(f"[Pipeline] Closing database connection for spider: {spider.name}")
        pass

    def process_item(self, item, spider):
        # Save item to database
        self.logger.info(f"[Pipeline] Saving item to database: {item}")
        return item